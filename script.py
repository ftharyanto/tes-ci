
# from js import console, document
import pandas as pd
from io import StringIO, BytesIO
from js import console, document, window, Blob
from pyodide.ffi import to_js

async def parse_text():
    raw_string = Element('source').element.value

    # wrap the string data in StringIO function
    StringData = StringIO(raw_string)
    
    
    # Print the dataframe
    clutters = ['List of real', '......']
    new_string = ''
    for line in StringData:
        if not any(clutter in line for clutter in clutters):
            new_string += line[3:]

    new_string = StringIO(new_string)
    df = pd.read_csv(new_string, sep ="|")
    # print(df)

    # # source = Element('source').element.value
    # # result = Element('result').element.value

    # remove spaces in columns name
    df.columns = df.columns.str.replace(' ','')

    # convert LatLon format
    lat = df.Lat.str.replace('S', '-1').str.replace('N', '1').str.split(' ', expand=True)[1].astype(float)
    factor = df.Lat.str.replace('S', '-1').str.replace('N', '1').str.split(' ', expand=True)[2].astype(float)
    df.Lat = lat * factor

    lon = df.Lon.str.replace('W', '-1').str.replace('E', '1').str.split(' ', expand=True)[1].astype(float)
    factor = df.Lon.str.replace('W', '-1').str.replace('E', '1').str.split(' ', expand=True)[2].astype(float)
    df.Lon = lon * factor

    # change column name
    df = df.rename(columns={'OriginTime(GMT)': 'Date'})

    # separate date and time
    date = df.iloc[:, 0].str.split(' ', expand=True)[0]
    df['Time'] = df.iloc[:, 0].str.split(' ', expand=True)[1]
    df.iloc[:, 0] = date

    # reorder columns
    df = df.drop(columns=['Status', 'cntP', 'TypeMag', 'cntM', 'AZgap', 'RMS'])
    cols = ['Date',
    'Time',
    'Lat',
    'Lon',
    'Depth',
    'Mag',
    'Remarks']
    df = df[cols]

    # remove km in depth column
    df['Depth'] = df['Depth'].str.replace(r'[^\d.]+', '', regex=True).astype(int)

    # declutter the rest
    # df.TypeMag = df.TypeMag.str.strip()
    # df.Status = df.Status.str.strip()
    df.Remarks = df.Remarks.str.strip()

    buf = BytesIO()
    df.to_csv(buf, index=False)
    await save_file(buf)


async def save_file(buf):
    try:
        # Read and convert to a JavaScript array
        buf.seek(0)
        content = to_js(buf.read())

        # Create a JavaScript Blob and set the Blob type as a CSV
        b = Blob.new([content], {type: "text/csv"})

        # Perform the actual file system save 
        fileHandle = await window.showSaveFilePicker()
        file = await fileHandle.createWritable()
        await file.write(b)
        await file.close()
    except Exception as e:
        console.log('Exception: ' + str(e))
        return

def tes_function():
    Element('tes').element.innerHTML = 'tes function'