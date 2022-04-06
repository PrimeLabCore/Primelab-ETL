import pandas as pd
import json
import base64
from sqlalchemy import create_engine
from datetime import datetime
import re

near_contracts = ['v1.nearapps.near', 'nft.nearapps.near', 'nearapps.near', 'v2.nearapps.near', 'file.nearapps.near',
                 'analytics.nearapps.near', 'escrow.nearapps.near', 'file-access.nearapps.near',
                 'send-near.nearapps.near', 'send-nft.nearapps.near']

engine = create_engine() # enter lookup table here


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
        # add a column to the dataframe with the current time
        txn_df['received_at_time'] = datetime.now()
        txn_df['block_timestamp'] = int.from_bytes(base64.b64decode(s['payload']['after']['block_timestamp']),
                                                   byteorder='big', signed=True)
        txn_df['nonce'] = int.from_bytes(base64.b64decode(s['payload']['after']['nonce']), byteorder='big', signed=True)
        txn_df['receipt_conversion_gas_burnt'] = int.from_bytes(
            base64.b64decode(s['payload']['after']['receipt_conversion_gas_burnt']), byteorder='big', signed=True)
        txn_df['receipt_conversion_tokens_burnt'] = int.from_bytes(
            base64.b64decode(s['payload']['after']['receipt_conversion_gas_burnt']), byteorder='big', signed=True)
        print(txn_df['receiver_account_id'])
        txn_df['contract_id'] = 'None'
        txn_df['user_id'] = 'None'
        txn_df['method_name'] = 'None'

        # lookup the txn_df['transaction_hash'] in the transactions_actions table in a database named 'mainnet',
        # if it exists collect the 'args' column and add it to the dataframe if it doesn't exist already skip this
        # step. if the value of txn_df['signer_account_id'] is in the near_contacts list, add the 'args' column to
        # the dataframe
        for x in range(len(near_contracts)):
            receiver_id = str(txn_df['receiver_account_id'][0])
            sender_id = str(txn_df['signer_account_id'][0])
            against = near_contracts[x]
            if (receiver_id or sender_id) == against:
                print('Near contract found!')
                transaction_lookup_hash = str(txn_df['transaction_hash'][0])
                # write the args column to the dataframe args is a dictionary
                args = pd.read_sql_query(
                    f"SELECT args FROM transaction_actions WHERE transaction_hash = '{transaction_lookup_hash}'",
                    engine)
                args_cleaned = args['args'][0]['args_json']
                args_cleaned = json.dumps(args_cleaned, indent=4)
                print(args_cleaned)
                args_json = json.loads(args_cleaned)
                #txn_df['json_args'] = args_json[0]
                try:
                    txn_df['contract_id'] = args_json['contract_id']
                    txn_df['method_name'] = args_json['method_name']
                    txn_df['user_id'] = args_json['nearapps_tags']['user_id']
                    print('👍')
                    
                except:
                    print('No contract id found')
                # Append the dataframe row to the parent dataframe
                if txn_df.empty == False:
                    txn_df_main = txn_df_main.append(txn_df, ignore_index=True)
                    print(txn_df_main)
                else:
                    print('No data found for this transaction')

    if txn_df_main.empty == False:
        target = create_engine() # enter your destination table below
        # write the dataframe to the db
        result = txn_df_main.to_sql('hybrid_transaction', schema='primelab', con=target, if_exists='append',
                                    index=False)
        results = {'data': txn_df_main, 'db_status': result}
        target.dispose()
        return json.loads(json.dumps(results, default=str))

    else:
        results = {'data': 'No Transactions', 'db_status': 'No'}
        return json.loads(json.dumps(results, default=str))