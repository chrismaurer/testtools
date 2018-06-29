__author__ = 'cmaurer'

import argparse
import os
import copy

class testotd():
    
    def __init__(self):

        # self.oc_log = r"/Users/cmaurer/testlog.log"

        for logfile in os.listdir(r"/var/log/debesys/"):
            if logfile.startswith("OC_") and logfile.endswith(".log"):
                self.oc_log = r"/var/log/debesys/" + logfile

        self.verify_data_list = []

        self.order_tags = { "account_code": "PARTY_ROLE_ACCOUNT_CODE",
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
        
        self.fix_order_type ={"35=D": "NewOrderSingle",
                              "35=F": "OrderCancelRequest",
                              "35=G": "OrderCancelReplaceRequest",
                              "35=8": "ExecutionReport",
                              "35=s": "NewOrderCross"}
        
        self.fix_tags ={"114": "PARTY_ROLE_DESK_ID",
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

        self.order_origination_mapping = {"0": "ORDER_ORIGINATION_OTHER_NON_DEA",
                                          "1": "ORDER_ORIGINATION_FROM_DIRECT_ACCESS_OR_SPONSORED_ACCESS_CUSTOMER"}

        self.order_capacity_mapping = {"0": "ORDER_CAPACITY_PRINCIPAL",
                                       "1": "ORDER_CAPACITY_RISKLESS_PRINCIPAL",
                                       "2": "ORDER_CAPACITY_AGENCY"}

    def optmenu(self):
    
        parser = argparse.ArgumentParser(description='Test Order Tag Defaults using order_id input from user.')
        parser.add_argument('-o', action='store', metavar='--order_id', help='order_id to be analysed.', type=str)
        order_id = parser.parse_args()
    
        return [order_id.o, ]

    def parse_log_message(self, log_data):

        """Parse TT logfile messages into a consistent, verifiable format"""

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
            elif "trans_type" in msg:
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

    def parse_fix_message(self, line):

        """Parse FIX logfile messages into a consistent, verifiable format"""

        log_message_dict = {}
        if "=" not in line[-1]:
            line.pop(-1)
        # if "35=s" in line:
        #     if "54=1" in line:
        #         log_msg_type = "FIX_" + self.fix_order_type[line[2]] + "-BUY"
        #     else:
        #         log_msg_type = "FIX_" + self.fix_order_type[line[2]] + "-SELL"
        # else:
        log_msg_type = "FIX_" + self.fix_order_type[line[2]]
        # log_message_dict = {k: v for k, v in (x.split('=') for x in line)}  # Not compatible with Python 2.6
        for x in line[3:]:
            keyval = x.split('=')
            log_message_dict[keyval[0]] = keyval[1]
    
        exec_type = log_msg_type
    
        return log_msg_type, log_message_dict, exec_type

    def parse_logfile_line(self, line):
    
        """Parse logfile messages into a usable format, remove unneeded messages and sort separate into TT or FIX"""

        if "8=FIX" in line:
            log_message = line.encode("ascii").split("\x01")
        else:
            if "OBDL (connection_id=" in line:
                line = line.replace(r")| Received", r") | Received |")
                line_list = line.split(" | ")[7:]
            else:
                line_list = line.split(" | ")[5:]

            if "order_submitter_inl.h" in line_list[0]:
                line_list.pop(0)

            if len(line_list) == 2:
                log_message = [line_list.pop(0)]
                log_message.extend(line_list[-1].split(" "))
            else:
                log_message = [line_list.pop(0), line_list.pop(0).lstrip(' ')]
                for line_element in range(1, len(line_list)):
                    log_message.append(line_list[line_element])
                log_message.extend(line_list[-1].split(" "))

            if "\n" in log_message[-1]:
                log_message.append(log_message.pop(-1).rstrip("\n"))
    
        return log_message

    def prep_messages(self, order_history, verbose=False, validate_fix=False):

        """Prepare messages for verification"""

        er_counter = 0
        cr_counter = 0
        tcr_counter = 0
        fixer_counter = 0
        fixcr_counter = 0

        for line in order_history:
            fix = False
            line = line.rstrip(r"\n")

            verification_dict = {}
            verification_list = []

            log_message = self.parse_logfile_line(line)
            if "8=FIX" in str(log_message):
                if not validate_fix:
                    pass
                else:
                    # if "35=s" in log_message:
                    #     buy_sell_split = log_message.index("54=2")
                    #     buy_log_message = log_message[:buy_sell_split]
                    #     sell_log_message = buy_log_message[0:19]
                    #     sell_log_message.extend(log_message[buy_sell_split:])
                    #     log_msg_type, log_message_dict, exec_type = self.parse_fix_message(buy_log_message)
                    #     log_msg_type, log_message_dict, exec_type = self.parse_fix_message(sell_log_message)
                    #     print "buy_log_message:", buy_log_message
                    #     print "sell_log_message:", sell_log_message
                    # else:
                    fix = True
                    log_msg_type, log_message_dict, exec_type = self.parse_fix_message(log_message)
            else:
                log_msg_type, log_message_dict, exec_type = self.parse_log_message(log_message)

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
            elif "TradeCaptureReport" in log_msg_type:
                tcr_counter += 1
                log_message_type = '-'.join([log_msg_type, str(tcr_counter)])
            else:
                log_message_type = log_msg_type

            print "\n" + "#" * 20
            print log_message_type, "-", exec_type
            print "#" * 20 + "\n"

            if fix:
                # Translate FIX Tags into TTUS Order Tags
                for k, v in log_message_dict.iteritems():
                    if k in self.fix_tags.keys():
                        log_message_dict[self.fix_tags[k]] = log_message_dict.pop(k)

                # Translate booleans to human readable
                for k, v in log_message_dict.iteritems():
                    if "ORDER_ATTRIBUTE" in k:
                        if log_message_dict[k] == "0":
                            log_message_dict[k] = "No"
                        if log_message_dict[k] == "1":
                            log_message_dict[k] = "Yes"
                    elif "order_capacity" in k:
                        log_message_dict[k] = self.order_capacity_mapping[log_message_dict[k]]
                    elif "order_origination" in k:
                        log_message_dict[k] = self.order_origination_mapping[log_message_dict[k]]
                    elif "PARTY_ROLE_DESK_ID" in k:
                        log_message_dict[k] = log_message_dict[k].split("|")[-1]

                if "PARTY_ROLE_ORDER_ENTRY_OPERATOR_ID" in log_message_dict:
                    log_message_dict["sAuthorizedTrader"] = log_message_dict["PARTY_ROLE_ORDER_ENTRY_OPERATOR_ID"].split("|")[-1]

                for k, v in log_message_dict.iteritems():
                    if k in self.fix_tags.values():
                        element = (k, v)
                        print element
                        verification_list.append(element)
            else:
                for element in log_message_dict.iteritems():
                    for k, v in self.order_tags.iteritems():
                        if k in str(element) or v in str(element):
                            print element
                            verification_list.append(element)
                            break

            if verbose:
                if fix:
                    print "\n\nLINE:", "  ".join(line.encode("ascii").split("\x01"))
                else:
                    print "\n\nLINE:", line

            verification_list.sort()
            verification_dict[log_message_type, exec_type] = verification_list
            self.verify_data_list.append(verification_dict)

    def verify_otd_data(self):

        """Get all logfile messages associated with the target orders and copy them to [order_history].

        Pass [order_history] to self.validate_messages()"""

        messages_to_ignore = ["CassandraMessageStore", "got working order_id", "om_order_responder_inl.h"]

        order_history = []
        verbose = True
        validate_fix = False

        fix_nos_messages = []
        fix_nos = None
        found_fix_nos = False
        exch_order_num = None
    
        logfile = open(self.oc_log, 'r')
        for line in logfile.readlines():
            try:
                # Ridiculous hack to catch lines that are not Order updates
                if len(line.split(" | ")[5].split(" ")) > 1:
                    pass
                elif any(message_to_ignore in line for message_to_ignore in messages_to_ignore):
                    pass
                else:
                    if validate_fix:
                        if all(fix_nos_element in line for fix_nos_element in ["Send:", "8=FIX"]):
                            if any(fix_nos_element in line for fix_nos_element in ["35=D", "35=s"]):
                                fix_nos_messages.append(line)
                                if len(fix_nos_messages) > 25:
                                    fix_nos_messages.pop(0)

                    if any(ordid in line for ordid in order_id):
                        if validate_fix:
                            for exch_order_number_field in ["secondary_cl_ord_id=", "secondary_report_id="]:
                                if exch_order_number_field in line:
                                    exch_order_num = ((line.split(exch_order_number_field)[1]).split(" ")[0]).replace('"', '')
                                    exch_order_num = None if exch_order_num == '' else exch_order_num
                                    if exch_order_num not in order_id:
                                        order_id.append(exch_order_num)

                            if exch_order_num is not None:
                                for fix_nos_message in fix_nos_messages:
                                    if exch_order_num in fix_nos_message:
                                        fix_nos = fix_nos_message
                            if not found_fix_nos and fix_nos is not None:
                                order_history.append(fix_nos)
                                found_fix_nos = True
                        order_history.append(line)

                        if "ORD_STATUS_CANCELED" in line:
                            break

            except:
                continue

        logfile.close()

        self.prep_messages(order_history, verbose, validate_fix)
        self.verify_messages()

    def verify_messages(self):

        """Verify all log messages"""

        nos_unsupported = ["ORDER_ATTRIBUTE_TYPE_LIQUIDITY_PROVISION_ACTIVITY_ORDER", "order_capacity",
                           "order_origination", "sAuthorizedTrader"]

        print "\n\n", "#"*30, "\nVerification Report:\n", "#"*30, "\n"

        for i in range(0, len(self.verify_data_list)-1):
            compare_count = 1
            loop_compare = 1
            # after = self.verify_data_list[i+1]
            if any(skip_validation in str(self.verify_data_list[i].keys()[0][1]).lower() for skip_validation in
                   ["ordercancelrequest", "ordercancelreplacerequest"]):
                continue
            elif "NewOrderCross" not in str(self.verify_data_list) and "trade_report_trans_type_new" in \
                    str(self.verify_data_list[i].keys()[0][1]).lower():
                continue
            while loop_compare <= compare_count:
                before = copy.deepcopy(self.verify_data_list[i])
                while any(skip_validation in str(self.verify_data_list[i+loop_compare].keys()[0][1]).lower() for
                          skip_validation in ["ordercancelrequest", "ordercancelreplacerequest"]):
                    loop_compare += 1
                if "NewOrderCross" not in str(self.verify_data_list) and "trade_report_trans_type_new" in \
                        str(self.verify_data_list[i+loop_compare].keys()[0][1]).lower():
                    loop_compare += 1

                after = copy.deepcopy(self.verify_data_list[i+loop_compare])
                loop_compare += 1

                # Work-around for false-failures comparing messages that aren't expected to be there
                # TODO: Clean this up
                if "newordersingle" in str([before.keys()[0][1], after.keys()[0][1]]).lower() and \
                        "exec_type_pending_new" in str([before.keys()[0][1], after.keys()[0][1]]).lower():
                    while "PARTY_ROLE" in str(before.values()[0]):
                        for party_role_message in before.values()[0]:
                            if "PARTY_ROLE" in str(party_role_message):
                                before.values()[0].remove(party_role_message)
                    while "PARTY_ROLE" in str(after.values()[0]):
                        for party_role_message in after.values()[0]:
                            if "PARTY_ROLE" in str(party_role_message):
                                after.values()[0].remove(party_role_message)
                    while any(message_to_skip in str(after.values()[0]) for message_to_skip in nos_unsupported):
                        for after_message in after.values()[0]:
                            if any(message_to_skip in after_message for message_to_skip in nos_unsupported):
                                after.values()[0].remove(after_message)

                self.verify_compare(before, after)
                if "fix" not in before.keys()[0][1].lower() and "fix" in after.keys()[0][1].lower():
                    compare_count += 1

    def verify_compare(self, before, after):

        comparison_pairs = ["new", "fix", "executionreport", "replace", "cancel", "tradecapturereport", "handling",
                            "trade", "suspend"]
        list_comparison = before.values() == after.values()

        # for comparison_pair in comparison_pairs:
            # if comparison_pair in str([before.keys()[0][1], after.keys()[0][1]]).lower() or \
            #                 comparison_pair == "replace" and "suspend" in str(after.keys()[0][1]).lower():
            # if (comparison_pair in str([before.keys()[0][1], after.keys()[0][1]]).lower() and
            #         all(comparison_pair in message_type for message_type in [str(before.keys()[0][1]).lower(),
            #                                                                  str(after.keys()[0][1]).lower()])) or \
            #         (comparison_pair == "replace" and "suspend" in str(after.keys()[0][1]).lower()):

        print "\n{0}\n{1} ({2}) and {3} ({4}) match: {5}\n".format("-"*56, before.keys()[0][0],
                                                                   before.keys()[0][1], after.keys()[0][0],
                                                                   after.keys()[0][1], list_comparison)
        if len(before.values()) == 0:
            print "{0} contains no order tags.".format(before.keys()[0][0])
            # continue
        elif len(after.values()) == 0:
            print "{0} contains no order tags.".format(after.keys()[0][0])
            # continue
        else:
            before_acct = None
            after_acct = None
            for verification_point in before.values()[0]:
                if verification_point not in after.values()[0]:
                    print "{0} {1} was not found in {2}".format(before.keys()[0][1], verification_point,
                                                                after.keys()[0][1])
                    if "account" in verification_point:
                        for acct in before.values()[0]:
                            if "account" in acct:
                                before_acct = acct
                        for acct in after.values()[0]:
                            if "account_override" in acct:
                                after_acct = acct

            for verification_point in after.values()[0]:
                if verification_point not in before.values()[0]:
                    print "{0} {1} was not found in {2}".format(after.keys()[0][1], verification_point,
                                                                before.keys()[0][1])
                    if "account" in verification_point:
                        for acct in after.values()[0]:
                            if "account" in acct:
                                after_acct = acct
                        for acct in before.values()[0]:
                            if "account_override" in acct:
                                before_acct = acct

            if before_acct is not None and after_acct is not None:
                print "\n{0} was matched to {1}".format(before_acct, after_acct)

order_id = testotd().optmenu()
# order_id = ["e0748fcb-8ebb-47fc-b744-d64296965f55", ]
testotd().verify_otd_data()