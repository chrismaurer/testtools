__author__ = 'cmaurer'

import argparse
import os
import copy

# oc_log = r"/Users/cmaurer/testlog.log"

for logfile in os.listdir(r"/var/log/debesys/"):
    if logfile.startswith("OC_") and logfile.endswith(".log"):
        oc_log = r"/var/log/debesys/" + logfile

verification_dict = {}
verify_data_list = []


order_tags={"account_code": "PARTY_ROLE_ACCOUNT_CODE",
            "account": "PARTY_ROLE_CUSTOMER_ACCOUNT",
            "authorized group id": "PARTY_ROLE_ORDER_ENTRY_OPERATOR_ID",
            "clearing_account": "PARTY_ROLE_CLEARING_ACCOUNT",
            "clearing_firm_id": "PARTY_ROLE_CLEARING_FIRM",
            "client": "PARTY_ROLE_EXECUTING_FIRM",
            "client_id": "PARTY_ROLE_CLIENT_ID",
            "commodity_derivative_indicator": "ORDER_ATTRIBUTE_TYPE_RISK_REDUCTION_ORDER",
            "cti": "CTI Code",
            "desk": "PARTY_ROLE_DESK_ID",
            "direct_electronic_access": "order_origination",
            "exchange_account": "Exchange Account",
            "execution_decision": "PARTY_ROLE_EXECUTING_TRADER",
            "giveup": "PARTY_ROLE_GIVEUP_CLEARING_FIRM",
            "investment_decision": "PARTY_ROLE_INVESTMENT_DECISION_MAKER",
            "liquidity_provision": "ORDER_ATTRIBUTE_TYPE_LIQUIDITY_PROVISION_ACTIVITY_ORDER",
            "mifid_id": "PARTY_ROLE_COMPOSITE_MIFID_ID",
            "nybot_house": "NYBOT House #",
            "sAuthorizedTrader": "sAuthorizedTrader",
            "sMemo": "sMemo",
            "sText1": "sText1",
            "sText2": "sText2",
            "sTextTT": "text_tt",
            "trader": "PARTY_ROLE_ENTERING_TRADER",
            "trading_capacity": "order_capacity",
            "wce_house": "wce_house"}

fix_order_type = {"35=D": "NewOrderSingle",
                  "35=F": "OrderCancelRequest",
                  "35=G": "OrderCancelReplaceRequest",
                  "35=8": "ExecutionReport",
                  "35=s": "NewOrderCross"}

fix_tags = {"114": "PARTY_ROLE_DESK_ID",
            "115": "PARTY_ROLE_EXECUTING_FIRM",
            "116": "PARTY_ROLE_ORDER_ENTRY_OPERATOR_ID",
            "144": "PARTY_ROLE_DESK_ID",
            "439": "PARTY_ROLE_CLEARING_FIRM",  # Clearing Firm ID, NYBOT House Number, WCE House Number
            "440": "PARTY_ROLE_CLEARING_ACCOUNT",
            "9121": "sMemo",
            "9195": "PARTY_ROLE_ACCOUNT_CODE",
            "9700": "order_origination",
            "9701": "order_capacity",
            "9702": "ORDER_ATTRIBUTE_TYPE_LIQUIDITY_PROVISION_ACTIVITY_ORDER",
            "9703": "ORDER_ATTRIBUTE_TYPE_RISK_REDUCTION_ORDER",
            "9704": "PARTY_ROLE_INVESTMENT_DECISION_MAKER",
            "9705": "PARTY_ROLE_EXECUTING_TRADER",
            "9706": "PARTY_ROLE_CLIENT_ID",
            "9707": "PARTY_ROLE_COMPOSITE_MIFID_ID",
            "9207": "account",
            "9208": "CTI Code",
            "sAuthorizedTrader": "sAuthorizedTrader"}
            # "9207": "PARTY_ROLE_ORDER_ENTRY_OPERATOR_ID",


def optmenu():

    parser = argparse.ArgumentParser(description='Test Order Tag Defaults using order_id input from user.')
    parser.add_argument('-o', action='store', metavar='--order_id', help='order_id to be analysed.', type=str)
    order_id = parser.parse_args()

    return [order_id.o, ]


def parse_log_message(log_data):

    should_not_validate = ['client_time_sent', 'connection_id', 'account_id']
    log_message_dict = {}
    log_msg_type = log_data[0]
    logmsg = log_data[1:]
    message_list = []
    bracketed_message_list = []
    bracketed_message = False
    exec_type = None

    concatenating = False
    for msg in logmsg:

        if any(unneeded_msg in msg for unneeded_msg in should_not_validate):
            continue

        # handle values containing spaces
        if '="' in msg:
            concatenate_string = [msg]
            concatenating = True
        elif concatenating and msg == '':
            concatenate_string.append(msg)
        elif concatenating and '"' in msg:
            concatenate_string.append(msg)
            concatenating = False
            msg = ' '.join(concatenate_string)

        msg = msg.rstrip() if "}" in msg else msg

        if "=" not in msg:
            if msg == "{":
                bracketed_message = True
                bracketed_message_list = []
            elif bracketed_message and msg == '}':
                message_list.append("&".join(bracketed_message_list))
                bracketed_message = False
            else:
                pass

        elif bracketed_message:
            bracketed_message_list.append(msg)

        else:
            message_list.append(msg)

        if "exec_type" in msg:
            exec_type = msg.split("=")[-1]

    if "\\n" in message_list[-1]:
        message_list.pop(-1)

    for message_list_item in message_list:
        message_list_item = message_list_item.replace('\"', '')
        message_list_item = message_list_item.replace('order_attribute_type=', '')
        message_list_item = message_list_item.replace('order_attribute_value=1', 'Yes')
        message_list_item = message_list_item.replace('order_attribute_value=0', 'No')
        # print message_list_item
        if "&" in message_list_item and "party" in message_list_item:
            dict_update = message_list_item.split("&")
            for item in dict_update:
                if "party_role=" in item:
                    k = item.replace('party_role=', '')
                if "party_id" in item:
                    v = item.replace('party_id=', '')
            log_message_dict[k] = v
        elif "&" in message_list_item and "party" not in message_list_item:
            if "v_string" in message_list_item:
                dict_update = message_list_item.split("&")
                for item in dict_update:
                    if "name" in item:
                        k = item.replace('name=', '')
                    if "v_string" in item:
                        v = item.replace('v_string=', '')
                log_message_dict[k] = v
            else:
                log_message_dict[message_list_item.split("&")[0].replace('\"', '')] = \
                    message_list_item.split("&")[1].replace('\"', '')
        else:
            log_message_dict[message_list_item.split("=")[0].replace('\"', '')] = \
                message_list_item.split("=")[1].replace('\"', '')

    exec_type = log_msg_type if exec_type == None else exec_type

    return log_msg_type, log_message_dict, exec_type


def parse_fix_message(line):

    log_message_dict = {}
    if "=" not in line[-1]:
        line.pop(-1)
    # if "35=s" in line:
    #     if "54=1" in line:
    #         log_msg_type = "FIX_" + fix_order_type[line[2]] + "-BUY"
    #     else:
    #         log_msg_type = "FIX_" + fix_order_type[line[2]] + "-SELL"
    # else:
    log_msg_type = "FIX_" + fix_order_type[line[2]]
    # log_message_dict = {k: v for k, v in (x.split('=') for x in line)}  # Not compatible with Python 2.6
    for x in line[3:]:
        keyval = x.split('=')
        log_message_dict[keyval[0]] = keyval[1]

    exec_type = log_msg_type

    return log_msg_type, log_message_dict, exec_type



def parse_logfile_line(line):

    if "8=FIX" in line:
        log_message = line.encode("ascii").split("\x01")
    else:
        line_list = line.split(" | ")[5:]
        if "order_submitter_inl.h" in line_list[0]:
            line_list.pop(0)
        if "secondary_cl_ord_id" in line:
            log_message = [line_list[0], line_list[1].lstrip(' ')]
            log_message.append(line_list[2])
            log_message.append(line_list[3])
            log_message.extend(line_list[4].split(" "))
        elif "TradeCaptureReportAck" in line:
            log_message = [line_list[0], line_list[1].lstrip(' ')]
            log_message.extend(line_list[2].split(" "))
        elif "TradeCaptureReport" in line:
            log_message = [line_list[0], line_list[1].lstrip(' ')]
            log_message.append(line_list[2])
            log_message.extend(line_list[3].split(" "))
        else:
            log_message = [line_list[0], line_list[1].lstrip(' ')]
            log_message.extend(line_list[2].split(" "))

        if "\n" in log_message[-1]:
            log_message.append(log_message.pop(-1).rstrip("\n"))

    return log_message


def validate_messages(line, verbose=False, validate_fix=False):

    fix = False
    er_counter = 0
    cr_counter = 0
    fixer_counter = 0
    fixcr_counter = 0

    verification_list = []
    line = line.rstrip(r"\n")
    log_message = parse_logfile_line(line)
    if "8=FIX" in str(log_message):
        if not validate_fix:
            pass
        else:
            # if "35=s" in log_message:
            #     buy_sell_split = log_message.index("54=2")
            #     buy_log_message = log_message[:buy_sell_split]
            #     sell_log_message = buy_log_message[0:19]
            #     sell_log_message.extend(log_message[buy_sell_split:])
            #     log_msg_type, log_message_dict, exec_type = parse_fix_message(buy_log_message)
            #     log_msg_type, log_message_dict, exec_type = parse_fix_message(sell_log_message)
            #     print "buy_log_message:", buy_log_message
            #     print "sell_log_message:", sell_log_message
            # else:
            fix = True
            log_msg_type, log_message_dict, exec_type = parse_fix_message(log_message)
    else:
        if "secondary_order_id" in line:
            exch_order_num = ((line.split("secondary_order_id=")[0]).split("=")[-1]).rstrip(" | ")
            exch_order_num = None if exch_order_num == '' else exch_order_num
            order_id.append(exch_order_num)
        log_msg_type, log_message_dict, exec_type = parse_log_message(log_message)

    # Prepare log messages for validation
    if "ExecutionReport" in log_msg_type:
        if fix:
            fixer_counter += 1
            log_message_type = '-'.join([log_msg_type, str(fixer_counter)])
        else:
            er_counter += 1
            log_message_type = '-'.join([log_msg_type, str(er_counter)])
    elif "OrderCancelReplaceRequest" in log_msg_type:
        if fix:
            fixcr_counter += 1
            log_message_type = '-'.join([log_msg_type, str(fixcr_counter)])
        else:
            cr_counter += 1
            log_message_type = '-'.join([log_msg_type, str(cr_counter)])
    else:
        log_message_type = log_msg_type

    print "\n" + "#" * 20
    print log_message_type, "-", exec_type
    print "#" * 20 + "\n"

    if fix:
        # Translate FIX Tags into TTUS Order Tags
        for k, v in log_message_dict.iteritems():
            if k in fix_tags.keys():
                log_message_dict[fix_tags[k]] = log_message_dict.pop(k)

        # Translate booleans to human readable
        for k, v in log_message_dict.iteritems():
            if "ORDER_ATTRIBUTE" in k:
                if log_message_dict[k] == "0":
                    log_message_dict[k] = "No"
                if log_message_dict[k] == "1":
                    log_message_dict[k] = "Yes"
            elif "order_capacity" in k:
                if log_message_dict[k] == "0":
                    log_message_dict[k] = "ORDER_CAPACITY_DEAL"
                if log_message_dict[k] == "1":
                    log_message_dict[k] = "ORDER_CAPACITY_MATCH"
                if log_message_dict[k] == "2":
                    log_message_dict[k] = "ORDER_CAPACITY_AGENCY"
            elif "order_origination" in k:
                if log_message_dict[k] == "0":
                    log_message_dict[k] = "ORDER_ORIGINATION_OTHER_NON_DEA"
                if log_message_dict[k] == "1":
                    log_message_dict[k] = "ORDER_ORIGINATION_OTHER_NON_DEA"
            elif "PARTY_ROLE_DESK_ID" in k:
                log_message_dict[k] = log_message_dict[k].split("|")[-1]

        if "PARTY_ROLE_ORDER_ENTRY_OPERATOR_ID" in log_message_dict:
            log_message_dict["sAuthorizedTrader"] = log_message_dict["PARTY_ROLE_ORDER_ENTRY_OPERATOR_ID"].split("|")[-1]


        for k, v in log_message_dict.iteritems():
            if k in fix_tags.values():
                element = (k, v)
                print element
                verification_list.append(element)
    else:
        for element in log_message_dict.iteritems():
            for k, v in order_tags.iteritems():
                if k in str(element) or v in str(element):
                    print element
                    verification_list.append(element)
                    break

    if verbose:
        if fix:
            print "\n\nLINE:", " ".join(line.encode("ascii").split("\x01"))
        else:
            print "\n\nLINE:", line

    verification_list.sort()
    verification_dict[log_message_type] = verification_list
    verify_data_list.append([log_message_type, exec_type])


def verify_otd_data(order_id):

    verbose = True
    validate_fix = True

    fix_nos = None
    found_fix_nos = False

    logfile = open(oc_log, 'r')
    for line in logfile.readlines():
        try:
            # Ridiculous hack to catch lines that are not Order updates
            if len(line.split(" | ")[5].split(" ")) > 1:
                continue
            if all(fix_nos_element in line for fix_nos_element in ["Send:", "8=FIX"]):
                if any(fix_nos_element in line for fix_nos_element in ["35=D", "35=s"]):
                    fix_nos = copy.copy(line)
            if any(ordid in line for ordid in order_id):
                if not found_fix_nos and fix_nos is not None:
                    # print "fix_nos:\n\n", fix_nos
                    validate_messages(fix_nos, verbose, validate_fix)
                    found_fix_nos = True
                validate_messages(line, verbose, validate_fix)

        except:
            continue

    # Verify messages
    print "\n\n", "#"*30, "\nVerification Report:\n", "#"*30, "\n"
    for i in range(0, len(verify_data_list)-1):
        if "OrderCancelReplaceRequest" in verify_data_list[i+1][0] and "REPLACED" in verify_data_list[i][1]:
            continue
        elif any(msgtype in verify_data_list[i+1][0] for msgtype in ["NewOrderSingle", "OrderCancelRequest"]):#,
            if "OrderCancelReplaceRequest" in verify_data_list[i+1][0] and ("REPLACED" in verify_data_list[i][1]):
                pass
            elif "OrderCancelRequest" in verify_data_list[i+1][0] and "REPLACE" in verify_data_list[i][1]:
                pass
            else:
                print "{0}\nComparing {1} with {2}\n".format("-"*56, verify_data_list[i+1][1], verify_data_list[i][1])
                for m in [i, i+1]:
                    if len(verification_dict[verify_data_list[m][0]]) == 0:
                        print "{0} contains no order tags.".format(verify_data_list[m][0])
                        break
                else:
                    for item in verification_dict[verify_data_list[i+1][0]]:
                        if item not in verification_dict[verify_data_list[i][0]]:
                            print "{0} {1} was not found in {2}".format(verify_data_list[i+1][1], item,
                                                                        verify_data_list[i][1])
                    if not item not in verification_dict[verify_data_list[i][0]]:
                        print "All order tags from {0} were found in {1}\n".format(verify_data_list[i+1][0],
                                                                                  verify_data_list[i][0])
        else:
            if "EXEC_TYPE_PENDING_REPLACE" in verify_data_list[i][1]:
                print "{0}\n{1} and {2} match: {3}\n".format(
                    "-"*56, verify_data_list[i][1], verify_data_list[i+1][1],
                    verification_dict[verify_data_list[i][0]] == verification_dict[verify_data_list[i+1][0]])
                for transaction in verify_data_list:
                    if "EXEC_TYPE_NEW" in transaction:
                        exec_new_idx = verify_data_list.index(transaction)
                print "{0}\nGoing back and confirming: T or F? {1} and {2} match: {3}\n".format(
                    "-"*56, verify_data_list[exec_new_idx][1], verify_data_list[i][1],
                    verification_dict[verify_data_list[exec_new_idx][0]] == verification_dict[verify_data_list[i][0]])
                if not verification_dict[verify_data_list[exec_new_idx][0]] == verification_dict[verify_data_list[i][0]]:
                    for item in verification_dict[verify_data_list[i][0]]:
                        if item not in verification_dict[verify_data_list[exec_new_idx][0]]:
                            print "{0} contains: {1}".format(verify_data_list[i], item)
                    for item in verification_dict[verify_data_list[exec_new_idx][0]]:
                        if item not in verification_dict[verify_data_list[i][0]]:
                            print "{0} contains: {1}".format(verify_data_list[exec_new_idx], item)
            else:
                index = 1
                while True:
                    if any("FIX_ExecutionReport" in validation_msg for validation_msg in [verify_data_list[i][1], verify_data_list[i+index][1]])\
                            and not all("FIX_" in validation_msg for validation_msg in [verify_data_list[i][1], verify_data_list[i+index][1]]):
                        break
                    print "{0}\n{1} and {2} match: {3}\n".format(
                        "-"*56, verify_data_list[i][1], verify_data_list[i+index][1],
                        verification_dict[verify_data_list[i][0]] == verification_dict[verify_data_list[i+index][0]])
                    if not verification_dict[verify_data_list[i][0]] == verification_dict[verify_data_list[i+index][0]]:
                        for m in [i, i+index]:
                            if len(verification_dict[verify_data_list[m][0]]) == 0:
                                print "{0} contains no order tags.".format(verify_data_list[m][0])
                                break
                        else:
                            for item in verification_dict[verify_data_list[i+index][0]]:
                                if item not in verification_dict[verify_data_list[i][0]]:
                                    print "{0} contains: {1}".format(verify_data_list[i+index], item)
                            for item in verification_dict[verify_data_list[i][0]]:
                                if item not in verification_dict[verify_data_list[i+index][0]]:
                                    print "{0} contains: {1}".format(verify_data_list[i], item)
                    if "FIX" not in verify_data_list[i+index][1]:
                        break
                    else:
                        index += 1

    logfile.close()

order_id = optmenu()
# order_id = ["c10f8b2d-068a-4d18-ad9f-741b8078858a", ]
verify_otd_data(order_id)