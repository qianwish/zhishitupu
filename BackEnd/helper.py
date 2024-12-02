class helper:
   @staticmethod
   def read_file(path):
       with open(path, encoding="utf-8") as f:
           while True:
               line = f.readline().strip()
               if not line:
                   break
               yield line
