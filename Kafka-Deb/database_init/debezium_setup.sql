-- The following should be run in the source indexer database

-- Create a role for the debezium user with replication privs
create role debezium_cdc with login password '3v43aXw625HS*DQ';
grant rds_replication to debezium_cdc;

-- Create a replication group role
-- This enables debezium to share ownership of the required tables with the current table owner
create role replication_group;
grant replication_group to postgres;
grant replication_group to debezium_cdc;

-- Create a publication for the tables we are interested in
create publication dbz_publication for table transactions, action_receipt_actions;

-- Create a heartbeat table
-- This helps with known issues where postgres wal gets clogged
create table public.debezium_heartbeat (heartbeat varchar not null);
-- Create a signal table
-- this is useful for sending messages to debezium e.g. to snapshot a new table
-- see https://debezium.io/blog/2021/10/07/incremental-snapshots/
create table public.debezium_signal (id varchar(64), type varchar(32), data varchar(2048));

-- Assign the required tables to the role so debezium has access
do $$
declare
    -- Any further tables should be added to this list
    l_table_list varchar[] := array['transactions', 'action_receipt_actions', 'debezium_heartbeat', 'debezium_signal', 'transaction_actions'];
    -- Change this if you have a different replication group name
    l_replication_role text := 'REPLICATION_GROUP';
    i record;
begin
    for i in (select schemaname||'.'||tablename tbl
                from pg_tables
                join unnest(l_table_list) tablename using (tablename)
               where schemaname = 'public')
    loop
       execute 'ALTER TABLE '||i.tbl||' OWNER TO '||l_replication_role;
    end loop;     
end
$$ language plpgsql;

