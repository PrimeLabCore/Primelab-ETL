from pydantic import BaseModel


class TransactionBase(BaseModel):
    transaction_hash: str
    included_in_block_hash: str
    included_in_chunk_hash: str
    index_in_chunk: int
    block_timestamp: int
    signer_account_id: str
    signer_public_key: str
    nonce: int
    receiver_account_id: str
    signature: str
    status: str
    converted_into_receipt_id: str
    receipt_conversion_gas_burnt: str
    receipt_conversion_tokens_burnt: str

