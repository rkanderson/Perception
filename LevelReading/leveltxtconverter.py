from PIL import Image

lvl = raw_input("Enter lvl id: ")

im = Image.open(lvl) #Can be many different formats.
pix = im.load()

print ("Image size="+str(im.size)) 
width=im.size[0]
height=im.size[1]

OUTPUT_STRING = "" #The level in the form of text!

#constants for converting pixel values to text
SPACE = (0,0,0) #EmptySpace (BLACK)
HASHTAG = (0, 0, 255) #Platform (BLUE)
S = (255,255,255) #PlayerSpawn (WHITE)
E = (0, 255, 0) #Exit (GREEN)
L = (255, 0, 0) #Lava (RED)
DOLLAR = (255, 255, 0) #Lock block (Yellow)
K = (255, 255, 100) #Key (Lighter Yellow)

for row in range(height):
	
	OUTPUT_STRING+="\""
	for col in range(width):
		px = pix[col, row]
		
		char_to_add = {
			SPACE: ' ',
			HASHTAG: '#',
			S: 'S',
			E: 'E',
			L: 'L'
		}.get(px, '?') # A ? will appear for unknown color->character relationships
		
		OUTPUT_STRING+=char_to_add

	OUTPUT_STRING+="~\"\\\n"


print ("Printing level...")
print OUTPUT_STRING
print ("[Done]")