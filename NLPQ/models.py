from typing import TypedDict

from sqlalchemy import Column, Integer, String, DateTime  # type: ignore

from .database import Base

class TransactionDict(TypedDict):
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



class Transaction(Base):
    """
    Defines the items model
    """

    __tablename__ = "stg_transactions"

    transaction_hash = Column(String, primary_key=True)
    included_in_block_hash = Column(String)
    included_in_chunk_hash = Column(String)
    index_in_chunk = Column(Integer)
    block_timestamp = Column(Integer)
    signer_account_id = Column(String)
    signer_public_key = Column(String)
    nonce = Column(Integer)
    receiver_account_id = Column(String)
    signature = Column(String)
    status = Column(String)
    converted_into_receipt_id = Column(String)
    receipt_conversion_gas_burnt = Column(String)
    receipt_conversion_tokens_burnt = Column(String)

    

    def __init__(self,
                 transaction_hash: str,
                included_in_block_hash: str,
                included_in_chunk_hash: str,
                index_in_chunk: int,
                block_timestamp: int,
                signer_account_id: str,
                signer_public_key: str,
                nonce: int,
                receiver_account_id: str,
                signature: str,
                status: str,
                converted_into_receipt_id: str,
                receipt_conversion_gas_burnt: str,
                receipt_conversion_tokens_burnt: str):
        
        self.transaction_hash = transaction_hash
        self.included_in_block_hash = included_in_block_hash
        self.included_in_chunk_hash = included_in_chunk_hash
        self.index_in_chunk = index_in_chunk
        self.block_timestamp = block_timestamp
        self.signer_account_id = signer_account_id
        self.signer_public_key = signer_public_key
        self.nonce = nonce
        self.receiver_account_id = receiver_account_id
        self.signature = signature
        self.status = status
        self.converted_into_receipt_id = converted_into_receipt_id
        self.receipt_conversion_gas_burnt = receipt_conversion_gas_burnt
        self.receipt_conversion_tokens_burnt = receipt_conversion_tokens_burnt


    def __repr__(self) -> str:
        return f"<Transaction {self.transaction_hash}>"

    @property
    def serialize(self) -> TransactionDict:
        """
        Return item in serializeable format
        """
        return {"transaction_hash": self.transaction_hash,
                "included_in_block_hash": self.included_in_block_hash,
                "included_in_chunk_hash": self.included_in_chunk_hash,
                "index_in_chunk": self.index_in_chunk,
                "block_timestamp": self.block_timestamp,
                "signer_account_id": self.signer_account_id,
                "signer_public_key": self.signer_public_key,
                "nonce": self.nonce,
                "receiver_account_id": self.receiver_account_id,
                "signature": self.signature,
                "status": self.status,
                "converted_into_receipt_id": self.converted_into_receipt_id,
                "receipt_conversion_gas_burnt": self.receipt_conversion_gas_burnt,
                "receipt_conversion_tokens_burnt": self.receipt_conversion_tokens_burnt
               }
