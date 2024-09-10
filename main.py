from src.config import log
from src.dataanalyticsprocessor import DataInterpreter


def main():
    # Instantiate the class and save results
    try:
        log.debug("##########################################################\
                 #       DATA ANALYTICS PROCESS HAS STARTED.........      #\
                 ##########################################################")
        data_interpreter = DataInterpreter()
        data_interpreter.save_results_to_csv()
        log.debug("       ##########################################################\
                         #       DATA ANALYTICS PROCESS HAS COMPLETED.........      #\
                         ##########################################################")
    except Exception as e:
        log.error(f"###########################################################\
                 #       DATA ANALYTICS PROCESS HAS AN ERROR:{e}.........     #\
                 ##############################################################")

if __name__ == '__main__':
    main()