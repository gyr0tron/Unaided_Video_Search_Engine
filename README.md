# Unaided Video Search Engine

**Folder Structure**

```bash

├───data
│   ├───processed
│   └───raw
├───model
├───notebook
├───src
│   ├───modelling
│   └───processing
└───test
```

- **data**
  - **processed**
    Storage for processed data ready to be used.
  - **raw**
    A local subset copy of retrieved data.
- **model**
  Storing intermediate results in here such as weights.
- **notebook**
- **src**
  - **modelling**
    Not just model construction and training but also evaluation.
  - **processing**
    Data ingestion and data transformation.
- **test**
  Place to test out snippets.

## Dependencies

- ffmpeg
- mkvmerge
- OpenCV
- PySceneDetect
- Numpy
- Click
- tqdm
