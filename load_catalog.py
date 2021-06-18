import json

print("JSON Loader for AV Movie Catalog")
with open('AV_Catalog.json','r') as f:
  data=json.load(f)
f.close()
print("\n This program will overwrite all data on existing AV_Catalog file.")
if input("Are you sure you wish to continue? y/n: ").lower()=='y':
  backup=data
  data.clear()
  index= int(input("Enter no. of Movies: "))
  if index<1:
    print("You Piece of Trash!")
    print("If I hadn't thought about this edge-case you would've just\ndeleted all data in the JSON file.")
    print("Donkey.")
  else:
    for i in range(index):
      name=input("Movie Name: ")
      if len(name)>256:
        print("Character Limit Exceeded. Terminating Operation.")
        data=backup
      else:
        synopsis=input("Synopsis: ")
        if len(synopsis)>2048:
          print("Character Limit Exceeded. Terminating Operation.")
          data=backup
        else:
          image_url=input("Poster URL: ")
          if not (image_url.startswith('http://') or image_url.startswith('https://')):
            print("Invalid URL Entered. URL must begin with http:// or https://, Terminating Operation")
            data=backup
          else:
            link=input("Drive Link: ")
            if not (link.startswith('http://') or link.startswith('https://')):
              print("Invalid URL Entered. URL must begin with http:// or https://, Terminating Operation")
              data=backup
            else:
              datum={
              'index':i,
              'name':name,
              'synopsis':synopsis,
              'image_url':image_url,
              'link':link
              }
              data.append(datum)
              print(data)
    
    if data!=backup:
      print("Data Collected, writing JSON")
    else:
      print("Restoring Data / No Change")

    with open('AV_Catalog.json','w') as f:  
      json.dump(data,f, indent=4)
    f.close()
    print("JSON File saved.")
else:
  print("Good choice.")
  print("Data currently on AV_Catalog: "+data)
  print("Come back later when ready.")
ex=input("Press any key to continue.")