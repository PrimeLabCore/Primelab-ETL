-------------------------------------------------
-- Tables
-------------------------------------------------
create table primelab.stg_transactions(
    transaction_hash                text
   ,included_in_block_hash          text
   ,included_in_chunk_hash          text
   ,index_in_chunk                  integer
   ,block_timestamp                 numeric(20,0)
   ,signer_account_id               text
   ,signer_public_key               text
   ,nonce                           numeric(20,0)
   ,receiver_account_id             text
   ,signature                       text
   ,status                          text
   ,converted_into_receipt_id       text
   ,receipt_conversion_gas_burnt    numeric(20,0)
   ,receipt_conversion_tokens_burnt numeric(45,0)
   ,received_at_time                timestamp
);

create table primelab.stg_action_receipt_actions(
    receipt_id                          text
   ,index_in_action_receipt             integer
   ,action_kind                         text
   ,args                                jsonb
   ,receipt_predecessor_account_id      text
   ,receipt_receiver_account_id         text
   ,receipt_included_in_block_timestamp numeric(20,0)
   ,slice_id                            text
   ,wallet_id                           text
   ,received_at_time                    timestamp
);


-------------------------------------------------
-- Constraints
-------------------------------------------------
