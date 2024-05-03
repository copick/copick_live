# CopickLive
CopickLive is a Dash Plotly server visualizing CZII ML challenge pickathon results with live updates.  


## Usage
**Python environment setup:**  
`pip install -r requirements.txt`.   

A copick configuration file and a json checkpoint file are needed, see explanation below:

**A copick configuration json file template**  
The file is used to generate a customized copick configuration file for each picker. See [copick example](https://github.com/uermel/copick).

**A json checkpoint file**     
The file is used to generate a task list for each picker. It contains 3 keywords, ensuring every tomogram sample get 2 people to work on (`start` becomes `start+tasks_per_person` when `repeat >= 2`). Below is an example:    
```
{  
    "start": 0,       
    "repeat": 1,    
    "tasks_per_person": 5    
}  
``` 

**How to deploy?**  
1. Edit the `conifg.ini` file.  
2. Run `python app.py` in the Python environment. Access the website at `http://localhost:8000` in the browser.

## GUI
**CopickLive website**
![CZII copick live update](assets/gui-1.png)

**Get Started window**
![CZII copick live update](assets/gui-2.png)