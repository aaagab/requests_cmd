## INPUT TYPES in REQUESTS LIBRARY
- json: set headers to application/json
- data: headers must be set manually

```python
# https://github.com/kennethreitz/requests/blob/083aa67a0d3309ebe37eafbe7bfd96c235a019cf/requests/models.py#L455
# prepare_body 455 set the body content and the content_type
if json:
    if data:
      pass
    else:
      content_type="application/json"
      json is compressed? complexjson.dumps into body, complex dump means that is convert even object into json.
      if body is not by it encodes to utf-8

if is_stream:
  # it is a stream when the iter has data attribute or data is not string, byte, list, tuple, mapping, apparently mapping is also dictionary
  # stream is then related to data.
  # the stream is then when using data has an iterator.
  files are not allowed
else:
  if files:
    files must have tuples otherwise an error is thrown meaning, files data has to be providen even for optional file probably.
    # then it is a multi_part file uploads.
    # encode_files 110 Build the body for a multipart/form-data request
    # encode_files get both data and files.
      # it takes data only not json and the content_type and body is reset too

      # Will successfully encode files when passed as a dict or a list of
      # tuples. Order is retained if data is a list of tuples but arbitrary
      # if parameters are supplied as a dict.
      # The tuples may be 2-tuples (filename, fileobj), 3-tuples (filename, fileobj, contentype)
      # or 4-tuples (filename, fileobj, contentype, custom_headers).

      # data must not be a string.
      # fields comes from data.
      # files comes from files
      # a new_fields list is created, adding first the encoded fields and then the files.
      new_fields list is formatted with boundary and return content_type is set to multipart/form-data; boundary={boundary}
  else:
    if data:
        then data is encoded inside body.
        if data is string:
            content_type=None
        else:
            content_type='application/x-www-form-urlencoded'

    then if content_type has been set in prepare_body and it has not been set already in the headers.
        then content_type is set in the headers.

```

data purpose is for either:    
- fields for multipleform data
- encoded body data
- stream of data

json:  
- json is not set if data is present
- json does not work with files
- json does not work with stream of data

files:  
- does not work with json
- does not work with streams
- may use optional data

Summary for data, json and files:  
it is either:  
data  
  maybe string or json  
  if string content_type must be set:  
  lets say to set content_type each time for data  
json  
  type json  
files  
  files may have a data field.  