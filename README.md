# EU-project

This project, through a longitudinal study that leverages CORDIS data from the first nine Framework Programmes, aims to understand integration and exploration dynamics in the European research network.
We build the network of collaborations between countries and we evaluate equity in fund distribution and integration of new participants over time. Moreover, we analyze the semantic space of the projects 
descriptions to understand and quantify how research progressively explores different areas of interest.
Finally, we compare fund distribution across different countries and topic, comparing academia and industry.

## Structure

```
├── Data                                   <- Folder for data
├── Networks EFTA countries                <- Folder containing networks graphs, networks maps, and edgelists
├── Data Analysis                          <- Data exploration                                  
│   └── Analysis                           <- Outputs folder 
├── Embedding Space                        <- Embedding space exploration
│   ├── Minimum Spanning Tree              <- Scripts for Minimum Spanning Tree
│   └── Topics                             <- Scripts for topic modeling and comparison academy and industry               
├── Network Analysis                       <- Scripts to create the networks and compute inequality, integration, and gravity model
│   ├── Gravity model                      <- Gravity model scripts and results
│   └── Analysis                           <- Outputs folder                                         
├── Geolocation                            <- Scripts for location identification
├── README.md
└── requirements.txt
```

## Installation

## Installation

1) Clone the repository:
   `git clone https://github.com/vorsanigo/Tweet2Geo.git`
2) Get the data from LINK and put them into the folder `Data`
3) In the cloned folder, create a virtual environment through the command `virtualenv venv` and activate it through `source venv/bin/activate`
4) Inside the virtual environment, install the requirements through `pip install -r requirements.txt`


## Execution
