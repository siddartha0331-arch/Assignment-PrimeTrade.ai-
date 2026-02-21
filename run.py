import pandas as pd
import numpy as np
import argparse
import yaml
import json
import time
import os
from datetime import datetime
import logging
import sys

def setup_logging(log_file):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def main():
  parser= argparse.ArgumentParser()
  parser.add_argument('--input',required =True,help='input Csv FIle')
  parser.add_argument('--config',required =True,help='Config YAML file')
  parser.add_argument('--output',required =True,help='Output Json File')
  parser.add_argument('--log-file',required =True,help='log FIle')
  args=parser.parse_args()

  setup_logging(args.log_file)



  logging.info("job Started")
  start_time=time.time()




  #load config
  try:
    logging.info(f"loading config from:{args.config}")
    if not os.path.exists(args.config):
      raise FileNotFoundError(f"config file not found:{args.config}")
    
    try:
      with open(args.config,'r')as f:
        config=yaml.safe_load(f)
      
    except yaml.YAMLError as e:
      raise ValueError(f"Invalid YAML format in config file:{e}")

    required_fields = ['seed','window','version']
    for field in required_fields:
      if field not in config:
        raise ValueError(f"Missing requires field in config: {field}")
    
    seed=config['seed']
    window=config['window']
    version=config['version']
    logging.info(f"config loaded : seed={seed},window={window},version={version}")
    np.random.seed(seed)

    logging.info(f"Random seed set to:{seed}")
    #Input file
    logging.info(f"loading data from {args.input}")
    if not os.path.exists(args.input):
      raise FileNotFoundError(f"Input file not found:{args.input}")

    try:
      df=pd.read_csv(args.input)
    except pd.errors.EmptyDataError:
      raise ValueError(f"Input file is empty:{args.input}")
    except pd.errors.ParserError as e:
      raise ValueError(f"Invalid parsing CSV:{e}")
    except Exception as e:
      raise ValueError(f"Error reading csv:{e}")

    if len(df)==0:
      raise ValueError(f"CSV file contains no data rows")

    if 'close' not in df.columns:
      raise ValueError(f"Missing required column 'close' in csv")

    logging.info(f"Data loaded :{len(df)}rows")

    logging.info(f"Calculating rolling mean with window ={window}and signal")
    df['rolling_mean']=df['close'].rolling(window=window).mean()
    df['signal']=(df['close']>df['rolling_mean']).astype(int)
    logging.info(f"Rolling mean calculated and signal generated")


    signal_rate=df['signal'].mean()
    rows_processed=len(df)
    latency_ms=int((time.time() - start_time)*1000)
    logging.info(f"Metrics : signal_rate = {signal_rate:.4f},rows_processed={rows_processed},latency_ms={latency_ms}")

    logging.info(f"Writing output to {args.output}")
    
    output = {
            "version": version,
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(signal_rate, 4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success"
        }
    with open(args.output,'w')as f:
      json.dump(output,f, indent=2)
    logging.info(f"Output written to {args.output}")

    print(json.dumps(output,indent=2))
    sys.exit(0)

  except FileNotFoundError as e:
    logging.error(f"File not found: {e}")
    output={
        "version":config.get('version','v1') if 'config' in locals() else 'v1',
        "status":"error",
        "error_message": str(e)
    }
    with open(args.output,'w')as f:
      json.dump(output,f,indent=2)
    print(json.dumps(output,indent=2))
    sys.exit(1)

  except ValueError as e:
    logging.error(f"Validation error:{e}")
    output={
        "version":config.get('version','v1') if 'config' in locals() else 'v1',
        "status":"error",
        "error_message": str(e)
    }

    with open(args.output,'w')as f:
      json.dump(output,f,indent=2)
    print(json.dumps(output,indent=2))
    sys.exit(1)


  except Exception as e:
    logging.error(f"Unexpected error:{e}")
    output={
        "version":config.get('version','v1') if 'config' in locals() else 'v1',
        "status":"error",
        "error_message": f"Unexpected error:{str(e)}"
    }
    with open(args.output,'w')as f:
      json.dump(output,f,indent=2)
    print(json.dumps(output,indent=2))
    sys.exit(1)

if __name__ == "__main__":
  main()