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

1) Clone the repository:
   `git clone https://github.com/vorsanigo/Tweet2Geo.git`
2) Get the data from LINK and put them into the folder `Data`
3) In the cloned folder, create a virtual environment through the command `virtualenv venv` and activate it through `source venv/bin/activate`
4) Inside the virtual environment, install the requirements through `pip install -r requirements.txt`


## Execution

The instructions to replicate the results follows

1) **Data analysis**
   - Inside folder `Data Analysis`:
      - Notebook `data_analysis.ipynb` 
      - Notebook `geographical_analysis.ipynb` for the number of projects per NUTS2 region and the cumulative density function of the number of projects per NUTS2 region
2) **Embedding Space analysis**:
   - Inside the folder `Embedding space`:
        - Inside the folder `Minimum Spanning Tree` run the different scripts to compute the MST length in the different cases
     - Inside the folder `Topics`:
       - Notebook `embeddings_analysis_description.ipynb` for analysis on the topics and generation of the image of the embedding space
       - Notebook `money_projects_topics_analysis.ipynb` for the comparison between academy and industry
3) **Inequality and Integration**:
   - Inside the folder `Network Analysis`:
        - Notebook `network_analysis.ipynb` to compute inequality, integration, and to create the maps of the networks
        - Notebook gravity_model.ipynb for the gravity model
  
