-------------------------------------------------
-- Tables
-------------------------------------------------
create table primelab.etl_audits (
    etl_audit_id    integer generated always as identity
   ,record_count    integer
   ,audit_timestamp timestamp default current_timestamp 
);

-------------------------------------------------
-- Constraint
-------------------------------------------------
alter table primelab.etl_audits add constraint etl_audits_pkey primary key (etl_audit_id);

-------------------------------------------------
-- Views
-------------------------------------------------
create or replace view public.finalised_transactions as
    select ara.receipt_id
          ,ara.args
          ,ara.wallet_id
          ,ara.slice_id
          ,t.transaction_hash
          ,t.included_in_block_hash
          ,t.block_timestamp
          ,t.status
      from public.stg_transactions t
      join public.stg_action_receipt_actions ara on t.converted_into_receipt_id = ara.receipt_id;

-------------------------------------------------
-- Procedures
-------------------------------------------------
create or replace procedure primelab.move_matched_rows()
as
$$
begin
    -- Create a temporary table so we get a consistent view of the transactions at this point
    create temporary table txn_rec_tmp (
        receipt_id              text
       ,args                    jsonb
       ,wallet_id               text
       ,slice_id                text
       ,transaction_hash        text
       ,included_in_block_hash  numeric(20,0)
       ,block_timestamp         timestamp
       ,status                  text
    ) on commit drop;
    
    insert into txn_rec_tmp (receipt_id, args, wallet_id, slice_id
                            ,transaction_hash, included_in_block_hash, block_timestamp, status)
    select receipt_id, args, wallet_id, slice_id
          ,transaction_hash, included_in_block_hash, to_timestamp(block_timestamp/ 1000000000), status 
      from public.finalised_transactions;

    -- Create receipts
    insert into primelab.receipts(receipt_id, block_hash, status, created_at)
    select receipt_id, included_in_block_hash, status, block_timestamp
      from txn_rec_tmp 
        on conflict (receipt_id) do nothing;
    
    -- Create wallets
    insert into primelab.wallets(wallet_id, persona_id, created_at)
    select wallet_id, 1, block_timestamp /* TO DO - change persona to be dynamic once we have personas */
      from txn_rec_tmp
     where wallet_id is not null
        on conflict (wallet_id) do nothing;
    
    -- Create transactions /*TO DO - Add stack_name*/
    with txn_ins as (
        insert into primelab.transactions(transaction_id, receipt_id, slice_name
                                         ,wallet_id, tags_json, created_at, status)
        select transaction_hash, receipt_id, slice_id, wallet_id, args, block_timestamp, status
          from txn_rec_tmp
            on conflict (transaction_id) do nothing
        returning transaction_hash
    )
    -- Write to audit table
    insert into primelab.etl_audit (record_count)
    select count(*)
      from txn_ins;

    -- Now delete these from the staging tables
    -- Commented out for now
    -- delete from public.stg_transactions as t
    --  using txn_rec_tmp as trt
    --  where t.transaction_hash = trt.transaction_hash;
    
    -- delete from public.stg_action_receipt_actions as ara
    --  using txn_rec_tmp as trt
    --  where ara.receipt_id = trt.receipt_id;
    
end;
$$ language plpgsql;

