import pandas as pd
import json
import base64
from sqlalchemy import create_engine
from datetime import datetime
import re
#import GraphDatabase as gdb
import psycopg2

near_contracts = ['v1.nearapps.near', 'nft.nearapps.near', 'nearapps.near', 'v2.nearapps.near', 'file.nearapps.near',
                  'analytics.nearapps.near', 'escrow.nearapps.near', 'file-access.nearapps.near',
                  'send-near.nearapps.near', 'send-nft.nearapps.near']


def lambda_handler(event, context):
    txn_df_main = pd.DataFrame()
    data = event
    data = data['records']["indexer.public.transactions-0"]
    for i in range(len(data)):
        s = json.loads(base64.b64decode(data[i]['value']).decode('utf-8'))
        transaction = str((s['payload']['after']))
        transaction = transaction.replace("'", '"')
        transaction_json = json.loads(transaction)
        txn_df = pd.json_normalize(transaction_json)
        # print the headers of the dataframe
        # print(txn_df.columns)
        # add a column to the dataframe with the current time
        txn_df['received_at_time'] = datetime.now()
        txn_df['contract_name'] = ''
        txn_df['user_id'] = ''
        txn_df['block_timestamp'] = int.from_bytes(base64.b64decode(s['payload']['after']['block_timestamp']),
                                                   byteorder='big', signed=True)
        txn_df['nonce'] = int.from_bytes(base64.b64decode(
            s['payload']['after']['nonce']), byteorder='big', signed=True)
        txn_df['receipt_conversion_gas_burnt'] = int.from_bytes(
            base64.b64decode(s['payload']['after']['receipt_conversion_gas_burnt']), byteorder='big', signed=True)
        txn_df['receipt_conversion_tokens_burnt'] = int.from_bytes(
            base64.b64decode(s['payload']['after']['receipt_conversion_gas_burnt']), byteorder='big', signed=True)
        # check the signer account id and reciever account id against the near contracts list if it is a match update the contract_name to the matching contract name
        if s['payload']['after']['signer_account_id'] in near_contracts:
            txn_df['contract_name'] = s['payload']['after']['signer_account_id']
            txn_df['user_id'] = s['payload']['after']['signer_account_id']
        elif s['payload']['after']['receiver_account_id'] in near_contracts:
            txn_df['contract_name'] = s['payload']['after']['receiver_account_id']
            txn_df['user_id'] = s['payload']['after']['receiver_account_id']
        else:
            txn_df['contract_name'] = 'unknown'
            txn_df['user_id'] = 'unknown'
        txn_df['signer_account_id'] = s['payload']['after']['signer_account_id']
        txn_df['receiver_account_id'] = s['payload']['after']['receiver_account_id']
        txn_df['converted_into_receipt_id'] = s['payload']['after']['converted_into_receipt_id']
        txn_df_main = txn_df_main.append(txn_df)
    
    
    #results_pg = write_to_db(txn_df_main, 'transactions_etl')
    results_redshift = write_to_redshift(txn_df_main, 'transactions_etl')
    return results_redshift


def write_to_db(df, table_name):
    target = create_engine(
        "postgresql://postgres:PrimeLab2022@indexermainnet.cluster-crvchkyemots.us-east-1.rds.amazonaws"
        ".com:5432/primelab_data")
    result = df.to_sql(table_name, schema='primelab',
                       con=target, if_exists='append', index=False)
    results = {'data': df, 'db_status': result}
    target.dispose()
    return json.loads(json.dumps(results, default=str))


def write_to_redshift(df, table_name):
    print("Writing to Redshift")
    # create a connection to redshift
    conn_string = "" # your redshift connection string here
    print("connecting to db")
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    print("obtained cursor")
    # create a table in redshift
    cur.execute(
        "CREATE TABLE IF NOT EXISTS transactions_etl (received_at_time timestamp, block_timestamp bigint, nonce bigint, "
        "receipt_conversion_gas_burnt bigint, receipt_conversion_tokens_burnt bigint, signer_account_id text, receiver_account_id text, "
        "converted_into_receipt_id text, contract_name text, user_id text)")

    # for each row in the dataframe write the data to redshift
    for index, row in df.iterrows():
        query = "INSERT INTO transactions_etl (received_at_time, contract_name, user_id, block_timestamp, nonce, " \
                "receipt_conversion_gas_burnt, receipt_conversion_tokens_burnt, signer_account_id, receiver_account_id, " \
                "converted_into_receipt_id) VALUES ('{}', '{}', '{}', {}, {}, {}, {}, '{}', '{}', '{}')".format(
            row['received_at_time'], row['contract_name'], row['user_id'], row['block_timestamp'], row['nonce'],
            row['receipt_conversion_gas_burnt'], row['receipt_conversion_tokens_burnt'], row['signer_account_id'],
            row['receiver_account_id'], row['converted_into_receipt_id'])
        cur.execute(query)
        conn.commit()

    cur.close()
    conn.close()
    print("connection_closed")
    # return db_status = 'success' if the dataframe is successfully written to the database
    results = {'data': df, 'db_status': 'success'}
    return json.loads(json.dumps(results, default=str))


# a function to write the data to a dynamodb table
def write_to_dynamodb(df, table_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    # for each row in the dataframe write the data to dynamodb
    for index, row in df.iterrows():
        table.put_item(Item=row.to_dict())
    results = {'data': df, 'db_status': 'success'}
    return json.loads(json.dumps(results, default=str))


# a function to write the data to neo4j
def write_to_neo4j(df, table_name):
    # create a connection to neo4j
    driver = GraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", "neo4j"))
    # create a session
    with driver.session() as session:
        # for each row in the dataframe write the data to neo4j
        for index, row in df.iterrows():
            session.run("CREATE (a:Transaction {received_at_time: '{}', contract_name: '{}', user_id: '{}', block_timestamp: {}, nonce: {}, "
                        "receipt_conversion_gas_burnt: {}, receipt_conversion_tokens_burnt: {}, signer_account_id: '{}', receiver_account_id: '{}', "
                        "converted_into_receipt_id: '{}'})".format(row['received_at_time'], row['contract_name'], row['user_id'], row['block_timestamp'], row['nonce'],
                                                                  row['receipt_conversion_gas_burnt'], row['receipt_conversion_tokens_burnt'], row['signer_account_id'],
                                                                  row['receiver_account_id'], row['converted_into_receipt_id']))
    results = {'data': df, 'db_status': 'success'}
    return json.loads(json.dumps(results, default=str))

