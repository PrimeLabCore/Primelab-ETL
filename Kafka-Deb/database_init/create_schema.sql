/* TO DO - Check tablespaces with devops */

/* TO DO - Check if devops are setting up accounts */

/* TO DO - Create users, create roles */
create schema primelab;

create role etl_user with login password 'C%JQ55bxd^CKkJ2Z^ybzb8%P5';
grant select, insert on primelab_data.public.stg_transactions to etl_user;
grant select, insert on primelab_data.public.stg_action_receipt_actions to etl_user;