import json
import base64
from algosdk import account, mnemonic, constants
from algosdk.v2client import algod
from algosdk.future import transaction
from algosdk.future.transaction import AssetConfigTxn, wait_for_confirmation, AssetTransferTxn
from algosdk.mnemonic import to_private_key

def generate_algorand_keypair():
    private_key, address = account.generate_account()
    print("My address: {}".format(address))
    print("My private key: {}".format(private_key))
    print("My passphrase: {}".format(mnemonic.from_private_key(private_key)))
#generate_algorand_keypair()

# Write down the address, private key, and the passphrase for later usage
private_key = ""
my_mnemonic = ""
my_address = "T5S5S6YDAMZDT4WPXPMZC6MOSWL2SVFOPOUVLW5J6XLV22QRPVUSKIH3FY"

def first_transaction_example(my_mnemonic, my_address):
    algod_address = "https://testnet-api.algonode.cloud"
    algod_client = algod.AlgodClient("", algod_address)

    print("My address: {}".format(my_address))
    private_key = mnemonic.to_private_key(my_mnemonic)
    print(private_key)
    account_info = algod_client.account_info(my_address)
    print("Account balance: {} microAlgos".format(account_info.get('amount')))

    # build transaction
    params = algod_client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    #params.flat_fee = constants.MIN_TXN_FEE 
    #params.fee = 1000
    receiver = "HZ57J3K46JIJXILONBBZOHX6BKPXEM2VVXNRFSUED6DKFD5ZD24PMJ3MVA"
    amount = 100000
    note = "Hello World".encode()

    unsigned_txn = transaction.PaymentTxn(my_address, params, receiver, amount, None, note)
    
    # sign transaction
    signed_txn = unsigned_txn.sign(private_key)

    # submit transaction
    txid = algod_client.send_transaction(signed_txn)
    print("Signed transaction with txID: {}".format(txid))

    # wait for confirmation 
    try:
        confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)  
    except Exception as err:
        print(err)
        return

    print("Transaction information: {}".format(
        json.dumps(confirmed_txn, indent=4)))
    print("Decoded note: {}".format(base64.b64decode(
        confirmed_txn["txn"]["txn"]["note"]).decode()))

    print("Starting Account balance: {} microAlgos".format(account_info.get('amount')) )
    print("Amount transfered: {} microAlgos".format(amount) )    
    print("Fee: {} microAlgos".format(params.fee) ) 

    account_info = algod_client.account_info(my_address)
    print("Final Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")
#first_transaction_example(my_mnemonic, my_address)

def create_asset(passphrase, asset_creator_address):
    algod_address = "https://testnet-api.algonode.cloud"
    algod_client = algod.AlgodClient("", algod_address)

    private_key = to_private_key(passphrase)

    txn = AssetConfigTxn(
                         sender=asset_creator_address,
                         sp=algod_client.suggested_params(),
                         total=1000,
                         default_frozen=False,
                         unit_name="LATINUM",
                         asset_name="latinum",
                         manager=asset_creator_address,
                         reserve=asset_creator_address,
                         freeze=asset_creator_address,
                         clawback=asset_creator_address,
                         url="https://path/to/my/asset/details", 
                         decimals=0
                        )
    # Sign with secret key of creator
    stxn = txn.sign(private_key)
    # Send the transaction to the network and retrieve the txid.
    try:
        txid = algod_client.send_transaction(stxn)
        print("Signed transaction with txID: {}".format(txid))
        # Wait for the transaction to be confirmed
        confirmed_txn = wait_for_confirmation(algod_client, txid, 4)  
        print("TXID: ", txid)
        print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))   
    except Exception as err:
        print(err)
    # Retrieve the asset ID of the newly created asset by first
    # ensuring that the creation transaction was confirmed,
    # then grabbing the asset id from the transaction.
    print("Transaction information: {}".format(
                                               json.dumps(confirmed_txn, indent=4)
                                              )
         )
    # print("Decoded note: {}".format(base64.b64decode(
    #     confirmed_txn["txn"]["txn"]["note"]).decode()))
    return confirmed_txn
asset_id = create_asset(my_mnemonic, my_address)["asset-index"]

def reconfig_asset(passphrase, asset_creator_address, asset_id):
    algod_address = "https://testnet-api.algonode.cloud"
    algod_client = algod.AlgodClient("", algod_address)
    
    private_key = to_private_key(passphrase)
    
    params = algod_client.suggested_params()
    # comment these two lines if you want to use suggested params
    # params.fee = 1000
    # params.flat_fee = True
    txn = AssetConfigTxn(
                         sender=asset_creator_address,
                         sp=params,
                         index=asset_id, 
                         manager=asset_creator_address,
                         reserve=asset_creator_address,
                         freeze=asset_creator_address,
                         clawback=asset_creator_address
                        )
    # sign by the current manager - Account 2
    stxn = txn.sign(private_key)
    # txid = algod_client.send_transaction(stxn)
    # print(txid)
    # Wait for the transaction to be confirmed
    # Send the transaction to the network and retrieve the txid.
    try:
        txid = algod_client.send_transaction(stxn)
        print("Signed transaction with txID: {}".format(txid))
        # Wait for the transaction to be confirmed
        confirmed_txn = wait_for_confirmation(algod_client, txid, 4) 
        print("TXID: ", txid)
        print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))   
    except Exception as err:
        print(err)
    print("Transaction information: {}".format(
                                               json.dumps(confirmed_txn, indent=4)
                                              )
         )
    return confirmed_txn
reconfig_asset(my_mnemonic, my_address, asset_id)

def opt_in_asset(passphrase, asset_creator_address, asset_id):
    # OPT-IN
    # Check if asset_id is in account's asset holdings prior
    # to opt-in
    algod_address = "https://testnet-api.algonode.cloud"
    algod_client = algod.AlgodClient("", algod_address)
    
    private_key = to_private_key(passphrase)

    params = algod_client.suggested_params()
    # comment these two lines if you want to use suggested params
    # params.fee = 1000
    # params.flat_fee = True
    account_info = algod_client.account_info(asset_creator_address)

    holding = None
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1    
        if (scrutinized_asset['asset-id'] == asset_id):
            holding = True
            break
    
    if not holding:
        # Use the AssetTransferTxn class to transfer assets and opt-in
        txn = AssetTransferTxn(
                               sender=asset_creator_address,
                               sp=params,
                               receiver=asset_creator_address,
                               amt=0,
                               index=asset_id
                              )
        stxn = txn.sign(private_key)
        # Send the transaction to the network and retrieve the txid.
        try:
            txid = algod_client.send_transaction(stxn)
            print("Signed transaction with txID: {}".format(txid))
            # Wait for the transaction to be confirmed
            confirmed_txn = wait_for_confirmation(algod_client, txid, 4) 
            print("TXID: ", txid)
            print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))    
        except Exception as err:
            print(err)
        # Now check the asset holding for that account.
        # This should now show a holding with a balance of 0.
        print("Transaction information: {}".format(
                                                   json.dumps(confirmed_txn, indent=4)
                                                  )
             )
    #return confirmed_txn
opt_in_asset(my_mnemonic, my_address, asset_id)

def destroy_asset(passphrase, asset_creator_address, asset_id):
    # DESTROY ASSET
    # With all assets back in the creator's account,
    # the manager destroys the asset.
    algod_address = "https://testnet-api.algonode.cloud"
    algod_client = algod.AlgodClient("", algod_address)
    
    private_key = to_private_key(passphrase)

    params = algod_client.suggested_params()
    # comment these two lines if you want to use suggested params
    # params.fee = 1000
    # params.flat_fee = True
       
    # Asset destroy transaction
    txn = AssetConfigTxn(
                         sender=asset_creator_address,
                         sp=params,
                         index=asset_id,
                         strict_empty_address_check=False
                        )
    # Sign with secret key of creator
    stxn = txn.sign(private_key)
    # Send the transaction to the network and retrieve the txid.
    # Send the transaction to the network and retrieve the txid.
    try:
        txid = algod_client.send_transaction(stxn)
        print("Signed transaction with txID: {}".format(txid))
        # Wait for the transaction to be confirmed
        confirmed_txn = wait_for_confirmation(algod_client, txid, 4) 
        print("TXID: ", txid)
        print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))     
    except Exception as err:
        print(err)
    # Asset was deleted.
    try:    
        print("Transaction information: {}".format(
                                                   json.dumps(confirmed_txn, indent=4)
                                                  )
             )
        # asset_info = algod_client.asset_info(asset_id)
    except Exception as e:
        print(e)
destroy_asset(my_mnemonic, my_address, asset_id)