# CopickLive
CopickLive is a Dash Plotly web server visualizing CZII ML challenge pickathon results with live updates.  

CopickLive main page
![CZII copick live update](assets/gui-1.png)

Get Started window
![CZII copick live update](assets/gui-2.png)


## Usage
**Python environment setup:**  
`pip install -r requirements.txt` 

Three configuration files are needed: the copick configuration file, json checkpoint file, and copicklive conifguration file. See explanation below:

**The copick configuration json file template**  
This file is a template for generating a customized copick configuration file for each picker. See [copick example](https://github.com/uermel/copick).

**The json checkpoint file**     
The file is used to generate a task list for each picker. It contains 3 keywords, ensuring every tomogram sample get 2 people to work on (`start` becomes `start+tasks_per_person` when `repeat >= 2`). Below is an example:    
```
{  
    "start": 0,       
    "repeat": 1,    
    "tasks_per_person": 5    
}  
``` 

**The CopickLive configuration file**   
This file contains paths for finding the copick configuration template and checkpoint file. It also includes the directory path where copick (overlay) outputs are saved.

```
[copick]
COPICK_CONFIG_PATH = path_to_copick_config_file.json

[counter]
COUNTER_FILE_PATH = path_to_checkpoint_file.json

[local]
LOCAL_FILE_PATH = path_to_copick_overlay_output
```




**How to deploy?**    
1. Run `python app.py` in the Python environment.     
2. You can access the website at `http://localhost:8000` in the web browser.



