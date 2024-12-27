# Скрипт экпортирования уязвимостей с помощью API MaxPatrol VM
# Данный скрипт предназначен только для образовательных и информационных целей. Авторы не несут ответственности за любой ущерб или убытки, возникшие в результате использования этого кода или его фрагментов.
# Используйте его на свой страх и риск. Рекомендуем тщательно проверять код перед использованием и не использовать его в производственной среде без тщательного тестирования и оценки его безопасности.
# Мы не можем гарантировать, что код будет работать без ошибок или отвечать вашим требованиям. Пожалуйста, будьте осторожны.

import argparse, csv, logging,sys,json,os, xlsxwriter
from api import MPCoreAPI


def read_config(path):
    if not os.path.exists(path):
        print("[ERROR] Can't find " + path)
        sys.exit(1)
    with open(path, encoding='utf-8') as fh:
        data = fh.read()
    return json.loads(data)

logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s:\t%(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename="export.log", level="DEBUG")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Export assets vulners to CSV.")
    parser.add_argument("--password", type=str, help="provide password for account connecting to MP Core")
    parser.add_argument("--config", type=str, help="provide config name to run query")
    #parser.add_argument('password', type=str, help="MP VM Core Password")
    args = parser.parse_args()


    if args.password: 
        passwd = args.password
    else:
        passwd = input("Provide password for MP Core:")

    config_path =""
    if args.config: 
        config_path = args.config
    else:
        config_path = "config.json"

    conf = read_config(config_path)

    vm_api = MPCoreAPI(conf["core_url"], conf["client_secret"], conf["core_user"], passwd, "3334", "443",conf["PDQL_query"],conf["selectedGroupIds"])
    vm_api.connect()
    result = vm_api.get_data()
    if not result:
        exit(1)
    logging.debug("Got result with len: " + str(len(result)))

    # Write results
    output_file_name = conf["output_file_name"]
    headers = conf["table_headers"]
    count = 0
    if conf["output_format"] == "Excel":
        # Build Excel output
        print ("exporting to Excel")
        output_file_name =output_file_name + ".xlsx"
        workbook = xlsxwriter.Workbook(output_file_name)
        worksheet = workbook.add_worksheet("VM_report")
        row = 0
        col = 0
        for item in (headers):
            worksheet.write(row, col, item)
            col += 1
        result = result.split('"\n')
        for item in result:
            if count == 0:
                count += 1
                continue
            result_split = item.replace('&quot;', "'")
            result_split = result_split.replace('"', "")
            result_split = result_split.split(";")
            col = 0
            for item in (result_split):
                worksheet.write(count, col, item)
                col += 1
            count += 1
        workbook.close()
    else:
        output_file_name =output_file_name + ".csv"
        print ("exporting to CSV")
        # Build CSV data
        
        with open(output_file_name, "w", newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(headers)

            result = result.split('"\n')
            for item in result:
                if count == 0:
                    count += 1
                    continue
                result_split = item.replace('&quot;', "'")
                result_split = result_split.replace('"', "")
                result_split = result_split.split(";")
                csv_writer.writerow(result_split)
                count += 1
    print("Finished export " + str(count-1) + " lines to:" + str(output_file_name))