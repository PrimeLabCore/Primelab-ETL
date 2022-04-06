-------------------------------------------------
-- Tables
-------------------------------------------------
create table primelab.contracts (
    contract_id   integer generated always as identity
   ,contract_name text not null
);

create table primelab.personas (
    persona_id   integer generated always as identity
   ,persona_name text not null
);

create table primelab.persona_history (
    persona_history_id integer generated always as identity
   ,persona_id         integer not null
   ,wallet_id          text    not null
   ,member_date        date    not null
);

create table primelab.receipts (
    receipt_id text      not null
   ,block_hash text      not null
   ,status     text      not null
   ,created_at timestamp not null
);

create table primelab.transactions (
    transaction_id text       not null
   ,receipt_id     text       not null
   ,slice_name     text
   ,stack_name     text
   ,wallet_id      text
   ,tags_json      jsonb      not null
   ,created_at     timestamp  not null
   ,status         text       not null
);

create table primelab.wallets (
    wallet_id  text    not null
   ,email      text    
   ,persona_id integer not null
   ,phone      text   
   ,created_at timestamp
);

-------------------------------------------------
-- Constraints
-------------------------------------------------
-- Primary
alter table primelab.contracts add constraint contracts_pkey primary key (contract_id);
alter table primelab.personas add constraint personas_pkey primary key (persona_id);
alter table primelab.persona_history add constraint persona_history_pkey primary key (persona_history_id);
alter table primelab.receipts add constraint receipts_pkey primary key (receipt_id);
alter table primelab.transactions add constraint transactions_pkey primary key (transaction_id);
alter table primelab.wallets add constraint wallets_pkey primary key (wallet_id);
-- Foreign
alter table primelab.persona_history add constraint persona_history_persona_id_fkey foreign key (persona_id) references primelab.personas (persona_id);
alter table primelab.persona_history add constraint persona_history_wallet_id_fkey foreign key (wallet_id) references primelab.wallets (wallet_id);
alter table primelab.transactions add constraint transactions_receipt_id_fkey foreign key (receipt_id) references primelab.receipts (receipt_id);
alter table primelab.transactions add constraint transactions_wallet_id_fkey foreign key (wallet_id) references primelab.wallets (wallet_id);

-------------------------------------------------
-- Indexes
-------------------------------------------------
create index persona_history_persona_id_idx on primelab.persona_history using btree (persona_id);
create index persona_history_wallet_id_idx on primelab.persona_history using btree (wallet_id);
create index persona_history_member_date_idx on primelab.persona_history using btree (member_date);
create index receipts_created_at_idx on primelab.receipts using btree (created_at);
create index receipts_status_idx on primelab.receipts using btree (status);
create index transactions_created_at_idx on primelab.transactions using btree (created_at);
create index transactions_receipt_id_idx on primelab.transactions using btree (receipt_id);
create index transactions_wallet_id_idx on primelab.transactions using btree (wallet_id);
create index transactions_status_idx on primelab.transactions using btree (status);
