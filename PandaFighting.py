'''
Panda Fighting Game
'''

from boa.interop.System.Storage import GetContext, Get, Put, Delete
from boa.interop.System.Runtime import CheckWitness, GetTime, Notify, Serialize, Deserialize, Log
from boa.interop.System.ExecutionEngine import GetExecutingScriptHash
from boa.interop.Ontology.Native import Invoke
from boa.interop.System.Blockchain import GetHeight, GetHeader, GetBlock
from boa.interop.System.Header import GetHash
from boa.builtins import *

owner = ToScriptHash('XXXXXXXXXXXXXXXXXX')

NAME = 'Fighting Panda'
SYMBOL = 'Panda'

OWNER_BALANCE_PREFIX = 'Balance'
OWNER_OF_ASSET_PREFIX = 'OwnerOf'
APPROVE_PREFIX = 'Approve'
INITED = 'Initialized'
ASSET_INDEX_PREFIX = 'Index'
TOTAL_ASSET_COUNT = 'TotalCount'
ASSET_ID_PREFIX = 'AssetID'
ONT_BALANCE_PREFIX = 'OntBalance'
BAMBOO_BALANCE = 'BambooBalance'
LAST_FEED_TIME = 'LastFeedTime'
LAST_ADVENTURE_TIME = 'LastADTime'
USER_ASSET_PREFIX = 'UserAsset'

QUANLITY_GOLD = 'GOLD'
QUANLITY_SILVER = 'SILVER'
QUANLITY_COPPER = 'COPPER'
QUANLITY_IRON = 'IRON'
QUANLITY_WOOD = 'WOOD'

ATTRIBUTE_ID = 'ID'
ATTRIBUTE_NAME = 'Name'
ATTRIBUTE_TYPE = 'Type'
ATTRIBUTE_LEVEL = 'Lv'
ATTRIBUTE_EXP = 'Exp'
ATTRIBUTE_ATK = 'Atk'
ATTRIBUTE_HP = 'HP'
ATTRIBUTE_HPMAX = 'HPMAX'
ATTRIBUTE_Qty = 'Qty'
ATTRIBUTE_Img = 'Image'
ATTRIBUTE_EXPCAP = 'ExpCap'


ctx = GetContext()

selfAddr = GetExecutingScriptHash()

def Main(operation, args):
    if operation == 'init':
        return init()
    if operation == 'name':
        return name()
    if operation == 'symbol':
        return symbol()
    if operation == 'balanceOf':
        if len(args) != 1:
            return False
        owner = args[0]
        return balanceOf(owner)
    if operation == 'getUserAssetID':
        if len(args) != 2:
            return False
        account = args[0]
        idx = args[1]
        return getUserAssetID(account, idx)
    if operation == 'ownerOf':
        if len(args) != 1:
            return False
        assetID = args[0]
        return ownerOf(assetID)
    if operation == 'transfer':
        if len(args) != 2:
            return False
        toAcct = args[0]
        assetID = args[1]
        return transfer(toAcct, assetID)
    if operation == 'transferMulti':
        return transferMulti(args)
    if operation == 'approve':
        if len(args) != 2:
            return False
        toAcct = args[0]
        assetID = args[1]
        return approve(toAcct, assetID)
    if operation == 'getApproved':
        if len(args) != 1:
            return False
        assetID = args[0]
        return getApproved(assetID)
    if operation == 'takeOwnership':
        if len(args) != 2:
            return False
        toAcct = args[0]
        assetID = args[1]
        return takeOwnership(toAcct, assetID)
    if operation == 'tokenMetadata':
        if len(args) != 1:
            return False
        assetID = args[0]
        return tokenMetadata(assetID)
    if operation == 'buyPanda':
        if len(args) != 1:
            return False
        account = args[0]
        return buyPanda(account)
    if operation == 'queryAssetIDByIndex':
        if len(args) != 1:
            return False
        idx = args[0]
        return queryAssetIDByIndex(idx)
    if operation == 'queryAssetByID':
        if len(args) != 1:
            return False
        assetID = args[0]
        return queryAssetByID(assetID)
    if operation == 'queryAssetCount':
        return queryAssetCount()
    if operation == 'buyBamboo':
        if len(args) != 2:
            return False
        account = args[0]
        ontcount = args[1]
        return buyBamboo(account, ontcount)
    if operation == 'getBambooBalance':
        if len(args) != 1:
            return False
        account = args[0]
        return getBambooBalance(account)
    if operation == 'feedPanda':
        if len(args) != 1:
            return False
        assetID = args[0]
        return feedPanda(assetID)
    if operation == 'adventure':
        if len(args) != 2:
            return False
        assetID = args[0]
        lv = args[1]
        return adventure(assetID, lv)

    if operation == 'withdraw':
        if len(args) != 1:
            return False
        account = args[0]
        return withdraw(account)

    return False


def init():
    '''
    initialize the assets
    :return:
    '''
    if not Get(ctx, INITED):
        Put(ctx, INITED, 'TRUE')
        return True
    return False


def name():
    '''
    Name of the asset
    :return:
    '''
    return NAME


def symbol():
    '''
    symbol of the asset
    :return:
    '''
    return SYMBOL


def balanceOf(owner):
    '''
    balance of owned the assets
    :param owner:
    :return:
    '''
    key = concatkey(OWNER_BALANCE_PREFIX, owner)
    return Get(ctx, key)


def getUserAssetID(account, idx):
    key = concatkey(concatkey(USER_ASSET_PREFIX, account), idx)
    return Get(ctx, key)


def ownerOf(assetID):
    '''
    owner of the asset
    :param assetID:
    :return:
    '''
    key = concatkey(OWNER_OF_ASSET_PREFIX, assetID)
    return Get(ctx, key)


def transfer(toAcct, assetID):
    '''
    transfer the asset to another address
    :param toAcct:
    :param assetID:
    :return:
    '''
    if checkToAcctAndAsset(toAcct, assetID) == False:
        return False

    key = concatkey(OWNER_OF_ASSET_PREFIX, assetID)
    oldowner = Get(ctx, key)
    removeUserAsset(oldowner, assetID)
    Put(ctx, key, toAcct)
    newbalance = increaseOwnerBalance(toAcct)
    addUserAsset(toAcct, assetID, newbalance)
    Notify(['transfer', oldowner, toAcct, assetID])

    return True


def transferMulti(args):
    '''
    multi transfer
    :param args:
    :return:
    '''
    for p in args:
        if len(p) != 2:
            return False
        if transfer(p[0], p[1]) == False:
            raise Exception('Multi transfer failed!')
    return True


def approve(toAcct, assetID):
    '''
    approve the asset to another address
    :param toAcct:
    :param assetID:
    :return:
    '''
    if checkToAcctAndAsset(toAcct, assetID) == False:
        return False

    assetOwner = ownerOf(assetID)
    if not assetOwner:
        return False

    key = concatkey(APPROVE_PREFIX, assetID)
    if not Get(ctx, key):
        Put(ctx, key, toAcct)
        Notify(['approve', assetOwner, toAcct, assetID])
        return True

    return False


def getApproved(assetID):
    '''
    get the approved address of the asset
    :param assetID:
    :return:
    '''
    key = concatkey(APPROVE_PREFIX, assetID)
    return Get(ctx, key)


def takeOwnership(toAcct, assetID):
    '''
    take the approved asset
    :param toAcct:
    :param assetID:
    :return:
    '''
    if CheckWitness(toAcct) == False:
        return False

    assetOwner = ownerOf(assetID)
    if not assetOwner:
        return False

    removeUserAsset(assetOwner, assetID)
    # key = concatkey(concatkey(APPROVE_PREFIX, assetOwner), assetID)
    key = concatkey(APPROVE_PREFIX, assetID)

    approver = Get(ctx, key)
    if approver != toAcct:
        return False

    Delete(ctx, key)
    ownerKey = concatkey(OWNER_OF_ASSET_PREFIX, assetID)
    Put(ctx, ownerKey, toAcct)
    newbalance = increaseOwnerBalance(toAcct)
    addUserAsset(toAcct, assetID, newbalance)
    Notify(['transfer', assetOwner, toAcct, assetID])

    return True


def concatkey(str1, str2):
    return concat(concat(str1, '_'), str2)


def checkToAcctAndAsset(toAcct, assetID):
    '''
    validation function
    :param toAcct:
    :param assetID:
    :return:
    '''
    if len(toAcct) != 20:
        return False
    owner = ownerOf(assetID)
    if not owner:
        return False
    if CheckWitness(owner) == False:
        return False
    return True


def increaseOwnerBalance(acct):
    '''
    increase the owner balance
    :param acct:
    :return:
    '''
    balance = balanceOf(acct)
    key = concatkey(OWNER_BALANCE_PREFIX, acct)
    Put(ctx, key, balance + 1)

    return balance + 1


def removeUserAsset(acct, assetID):
    balance = balanceOf(acct)
    key = concatkey(OWNER_BALANCE_PREFIX, acct)
    Put(ctx, key, balance - 1)

    for i in range(1, balance + 1):
        tmpkey = concatkey(concatkey(USER_ASSET_PREFIX, acct), i)
        tmpassetID = Get(ctx, tmpkey)
        if tmpassetID == assetID:
            if i == balance:
                Delete(ctx, tmpkey)
            else:
                lastkey = concatkey(concatkey(USER_ASSET_PREFIX, acct), balance)
                lastAssetID = Get(ctx, lastkey)
                Put(ctx, tmpkey, lastAssetID)
                Delete(ctx, lastkey)
            return True
    return True



def addUserAsset(acct, assetID, idx):
    key = concatkey(concatkey(USER_ASSET_PREFIX, acct), idx)
    Put(ctx, key, assetID)


def tokenMetadata(assetID):
    '''
    this should be replaced by queryAssetByID
    :param assetID:
    :return:
    '''
    #for example
    return concatkey("tokenMetadata", assetID)


def createRandomPanda():
    '''
    create a new asset
    :param name:
    :param url:
    :param type:
    :return:
    '''
    timestamp = GetTime()
    totalcount = Get(ctx, TOTAL_ASSET_COUNT)
    Put(ctx, TOTAL_ASSET_COUNT, totalcount + 1)
    tmp = concatkey(concatkey(selfAddr, timestamp), totalcount + 1)
    assetID = sha256(tmp)
    # asset = {'ID': assetID, 'Name': name, 'Image': url, 'Type': type}
    seed = abs(getRandom())
    panda = createPanda(assetID, seed)

    Put(ctx, concatkey(ASSET_INDEX_PREFIX, totalcount + 1), assetID)
    Put(ctx, concatkey(ASSET_ID_PREFIX, assetID), Serialize(panda))
    return assetID


def createPanda(assetID, seed):
    rand = abs(sha256(seed))
    quanlity = QUANLITY_WOOD
    if seed % 1000 == 1:
        quanlity = QUANLITY_GOLD
    elif seed % 1000 <= 10:
        quanlity = QUANLITY_SILVER
    elif seed % 1000 <= 100:
        quanlity = QUANLITY_COPPER
    elif seed % 1000 <= 400:
        quanlity = QUANLITY_IRON


    names = ['SHARK','KITTY','HOHO','KAMY','LONG','KING','YOYO']
    idx = rand % len(names)

    panda = {'ID': assetID,
             'Name': concatkey('PANDA', names[idx]),
             'Type': 'PANDA',
             'Lv': 1,
             'Exp': 0,
             'ExpCap': 60,
             'Atk': 1,
             'HP': 10,
             'HPMAX': 10,
             'Qty': quanlity,
             'Image': concat(quanlity, '.png')}
    return panda




def buyPanda(account):
    '''
    buy an asset by any user
    :param account:
    :param assetID:
    :return:
    '''
    if CheckWitness(account) == False:
        return False
    if transferONT(account, selfAddr, 1):
        assetID = createRandomPanda()
        key = concatkey(OWNER_OF_ASSET_PREFIX, assetID)
        Put(ctx, key, account)
        newbalance = increaseOwnerBalance(account)
        addUserAsset(account, assetID, newbalance)
        ontbalance = Get(ctx, ONT_BALANCE_PREFIX)
        Put(ctx, ONT_BALANCE_PREFIX, ontbalance + 1)
        Notify(['transfer', '', account, assetID])
        return True
    return False


def queryAssetIDByIndex(idx):
    '''
    query assetid by index
    :param idx:
    :return:
    '''
    return Get(ctx, concatkey(ASSET_INDEX_PREFIX, idx))


def queryAssetByID(assetID):
    '''
    query asset detail by assetID
    :param assetID:
    :return:
    '''
    return Get(ctx, concatkey(ASSET_ID_PREFIX, assetID))


def queryAssetCount():
    '''
    query total count of assets
    :return:
    '''
    return Get(ctx, TOTAL_ASSET_COUNT)


def transferONT(fromacct, toacct, amount):
    """
    transfer ONT
    :param fromacct:
    :param toacct:
    :param amount:
    :return:
    """
    # ONT native contract address
    contractAddress = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01')

    if CheckWitness(fromacct):
        param = state(fromacct, toacct, amount)
        res = Invoke(0, contractAddress, 'transfer', [param])

        if res and res == b'\x01':
            return True
        else:
            return False

    else:
        return False


def transferONTFromContract(toacct, amount):
    """
    transfer ONT from contract
    :param fromacct:
    :param toacct:
    :param amount:
    :return:
    """
    # ONT native contract address
    contractAddress = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01')

    param = state(selfAddr, toacct, amount)
    res = Invoke(0, contractAddress, 'transfer', [param])

    if res and res == b'\x01':
        return True
    else:
        return False


def withdraw(account):
    '''
    withdraw ont to admin
    :param account:
    :return:
    '''
    if CheckWitness(account) == False:
        return False
    ontbalance = Get(ctx, ONT_BALANCE_PREFIX)
    if ontbalance > 0:
        if transferONTFromContract(account, ontbalance):
            Delete(ctx, ONT_BALANCE_PREFIX)
            return True
        else:
            return False
    return False


def getRandom():
    time = GetTime()
    height = GetHeight()
    header = GetHeader(height)

    return sha256(abs(GetHash(header)) % time)


def buyBamboo(account, ontcount):
    if CheckWitness(account) == False:
        return False
    if transferONT(account, selfAddr, ontcount):
        bbBalance = Get(ctx, concatkey(BAMBOO_BALANCE, account))
        Put(ctx, concatkey(BAMBOO_BALANCE, account), bbBalance + 10 * ontcount)
        return True
    return False


def getBambooBalance(account):
    return Get(ctx, concatkey(BAMBOO_BALANCE, account))


def feedPanda(assetID):
    '''
    feedPanda only recovery the HP loss
    :param assetID:
    :return:
    '''
    owner = ownerOf(assetID)
    if not owner:
        return False
    if CheckWitness(owner) == False:
        return False

    pdata = Get(ctx, concatkey(ASSET_ID_PREFIX, assetID))
    panda = Deserialize(pdata)
    if panda[ATTRIBUTE_HP] == panda[ATTRIBUTE_HPMAX]:
        return True
    else:
        bamboo = Get(ctx, concatkey(BAMBOO_BALANCE, owner))
        if bamboo < 1:
            return False
        increaseHP = 10 + abs(getRandom()) % 3
        if panda[ATTRIBUTE_HP] + increaseHP >= panda[ATTRIBUTE_HPMAX]:
            panda[ATTRIBUTE_HP] = panda[ATTRIBUTE_HPMAX]
        else:
            panda[ATTRIBUTE_HP] = panda[ATTRIBUTE_HP] + increaseHP
        Put(ctx, concatkey(ASSET_ID_PREFIX, assetID), Serialize(panda))
    return True


def adventure(assetID, lv):
    owner = ownerOf(assetID)
    if not owner:
        return False
    if CheckWitness(owner) == False:
        return False

    lastADTime = Get(ctx, concatkey(LAST_ADVENTURE_TIME, assetID))
    currentTime = GetTime()
    period = currentTime - lastADTime

    pdata = Get(ctx, concatkey(ASSET_ID_PREFIX, assetID))
    panda = Deserialize(pdata)
    if panda[ATTRIBUTE_HP] == 0:
        return False
    pandaLV = panda[ATTRIBUTE_LEVEL]
    qty = panda[ATTRIBUTE_Qty]
    # canAD = False
    # if qty == QUANLITY_GOLD:
    #     if period > 5 * 60:
    #         canAD = True
    # elif qty == QUANLITY_SILVER:
    #     if period > 10 * 60:
    #         canAD = True
    # elif qty == QUANLITY_COPPER:
    #     if period > 30 * 60:
    #         canAD = True
    # elif qty == QUANLITY_IRON:
    #     if period > 60 * 60:
    #         canAD = True
    # elif qty == QUANLITY_WOOD:
    #     if period > 90 * 60:
    #         canAD = True
    #
    # if canAD == False:
    #     return False

    tmpRandom = (abs(getRandom()) >> (lv % 5 + 1)) % (panda[ATTRIBUTE_HPMAX] + lv + pandaLV)
    magicno = abs(sha1(getRandom() >> (lv % 8 + 1))) % (pandaLV + lv)

    resist = (panda[ATTRIBUTE_ATK] * 35 + panda[ATTRIBUTE_HPMAX] / 10 * 50 + magicno * 20) / (panda[ATTRIBUTE_ATK] + panda[ATTRIBUTE_HPMAX] / 10 + pandaLV - lv)
    injuredHP = (tmpRandom * 100 - resist) / 100

    passed = False
    if injuredHP >= panda[ATTRIBUTE_HP]:
        panda[ATTRIBUTE_HP] = 0
    else:
        passed = True
        panda[ATTRIBUTE_HP] = panda[ATTRIBUTE_HP] - injuredHP
        gotExp = abs(sha1(getRandom() >> (lv % 8 + 1))) % 10
        newExp = panda[ATTRIBUTE_EXP] + gotExp
        if newExp >= panda[ATTRIBUTE_EXPCAP]:
            panda = levelUp(panda, panda[ATTRIBUTE_EXP] + gotExp - panda[ATTRIBUTE_EXPCAP])
        else:
            panda[ATTRIBUTE_EXP] = newExp
    Put(ctx, concatkey(ASSET_ID_PREFIX, assetID), Serialize(panda))


def getExpCap(lv):
    return lv * (lv + 5) * 10


def levelUp(panda, exceedExp):
    currentLv = panda[ATTRIBUTE_LEVEL]
    panda[ATTRIBUTE_LEVEL] = currentLv + 1
    panda[ATTRIBUTE_EXP] = exceedExp
    qty = panda[ATTRIBUTE_Qty]
    rand = abs(sha1(getRandom()))
    if qty == QUANLITY_GOLD:
        atk = panda[ATTRIBUTE_ATK]
        panda[ATTRIBUTE_ATK] = atk + rand % 6 + 6
        rand = rand >> 2
        hp = panda[ATTRIBUTE_HPMAX]
        panda[ATTRIBUTE_HPMAX] = hp + rand % 10 + 10
    if qty == QUANLITY_SILVER:
        atk = panda[ATTRIBUTE_ATK]
        panda[ATTRIBUTE_ATK] = atk + rand % 5 + 5
        rand = rand >> 4
        hp = panda[ATTRIBUTE_HPMAX]
        panda[ATTRIBUTE_HPMAX] = hp + rand % 8 + 8
    if qty == QUANLITY_COPPER:
        atk = panda[ATTRIBUTE_ATK]
        panda[ATTRIBUTE_ATK] = atk + rand % 4 + 4
        rand = rand >> 6
        hp = panda[ATTRIBUTE_HPMAX]
        panda[ATTRIBUTE_HPMAX] = hp + rand % 6 + 6
    if qty == QUANLITY_IRON:
        atk = panda[ATTRIBUTE_ATK]
        panda[ATTRIBUTE_ATK] = atk + rand % 3 + 3
        rand = rand >> 8
        hp = panda[ATTRIBUTE_HPMAX]
        panda[ATTRIBUTE_HPMAX] = hp + rand % 5 + 5
    if qty == QUANLITY_WOOD:
        atk = panda[ATTRIBUTE_ATK]
        panda[ATTRIBUTE_ATK] = atk + rand % 2 + 1
        rand = rand >> 10
        hp = panda[ATTRIBUTE_HPMAX]
        panda[ATTRIBUTE_HPMAX] = hp + rand % 4 + 4
    panda[ATTRIBUTE_HP] = panda[ATTRIBUTE_HPMAX]
    panda[ATTRIBUTE_EXPCAP] = getExpCap(currentLv + 1)
    return panda

