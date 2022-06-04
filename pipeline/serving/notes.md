Scratch work to get serving up with conda

```
   29  curl -o install.sh https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh
   30  bash install.sh
   31  bash install.sh -u
   32  mlflow models serve -m runs:/10f77abca3994387b52033d324401670/model -p 1234
   33  which conda
   34  source ~/.bashrc
   35  which conda
   36  mlflow models serve -m runs:/10f77abca3994387b52033d324401670/model -p 1234
   37  mlflow models serve -m runs:/10f77abca3994387b52033d324401670/model -p 1234 &
   38  curl http://127.0.0.1:1234
   39  jobs
   40  curl -sv http://127.0.0.1:1234
   41  curl -X POST -H "Content-Type:application/json; format=pandas-split" --data '{"columns":["alcohol", "chlorides", "citric acid", "density", "fixed acidity", "free sulfur dioxide", "pH", "residual sugar", "sulphates", "total sulfur dioxide", "volatile acidity"],"data":[[12.8, 0.029, 0.48, 0.98, 6.2, 29, 3.33, 1.2, 0.39, 75, 0.66]]}' http://127.0.0.1:1234/invocations
   42  curl -X POST -H "Content-Type:application/json; format=pandas-split" --data '{"columns":["temp"],"data":[[12.8]]}' http://127.0.0.1:1234/invocations
   43  history
```