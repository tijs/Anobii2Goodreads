# Customise these variables to define input and output
anobii_file = "export.csv"
goodreads_file = "import_to_goodreads.csv" 

####### do not change anything below this line

from datetime import date
import csv, codecs, cStringIO

class UTF8Recoder:
	"""
	Iterator that reads an encoded stream and reencodes the input to UTF-8
	"""
	def __init__(self, f, encoding):
		self.reader = codecs.getreader(encoding)(f)
	
	def __iter__(self):
		return self
	
	def next(self):
		return self.reader.next().encode("utf-8")

class UnicodeReader:
	"""
	A CSV reader which will iterate over lines in the CSV file "f",
	which is encoded in the given encoding.
	"""
	
	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		f = UTF8Recoder(f, encoding)
		self.reader = csv.reader(f, dialect=dialect, **kwds)
	
	def next(self):
		row = self.reader.next()
		return [unicode(s, "utf-8") for s in row]
	
	def __iter__(self):
		return self

class UnicodeWriter:
	"""
	A CSV writer which will write rows to CSV file "f",
	which is encoded in the given encoding.
	"""
	
	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		# Redirect output to a queue
		self.queue = cStringIO.StringIO()
		self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
		self.stream = f
		self.encoder = codecs.getincrementalencoder(encoding)()

	def writerow(self, row):
		items = []
		for s in row:
			if type(s) == type(u"s"):
				items.append(s.encode("utf8"))
			else:
				items.append(s)

		self.writer.writerow(items)
		# Fetch UTF-8 output from the queue ...
		data = self.queue.getvalue()
		data = data.decode("utf-8")
		# ... and reencode it into the target encoding
		data = self.encoder.encode(data)
		# write to the target stream
		self.stream.write(data)
		# empty queue
		self.queue.truncate(0)

	def writerows(self, rows):
		for row in rows:
			self.writerow(row)


reader = UnicodeReader(open(anobii_file,"rb"))
reader.next() # first line is column titles
target = []
target.append(["Title","Author","Additional Authors","ISBN","ISBN13","My Rating","Average Rating","Publisher","Binding","Year Published","Original Publication Year","Date Read","Date Added","Bookshelves","My Review","Spoiler","Private Notes","Recommended For","Recommended By"])
# loading all in memory is not efficient, there's certainly a better way
for l in reader:
	isbn = l[0].replace("'","")
	title = l[1] + ":" + l[2]
	author = l[3]
	format = l[4]
	pages = l[5]
	publisher = l[6]
	# expensive date conversion, but might come handy in future
	pubdate = ""
	#pd_tmp = l[7].replace("'","").split("-")
	#if pd_tmp[0]:
	#	pubdate = date(int(pd_tmp[0]),int(pd_tmp[1]),int(pd_tmp[2])).year 
	privnote = l[8]
	comment = l[10]
	status = l[11]
	readdate = ""
	if status[0:9] == "Finished:":
		readdate = status[10:] # can't be bothered to reformat here
	rating = l[12]
	tags = l[13].replace(" ","-").replace("-/-"," ")
	
	tline = [title,author,"",isbn,"",rating,"",publisher,format,"",pubdate,readdate,"",tags, comment,"",privnote,"",""]
	target.append(tline)

writer = UnicodeWriter(open(goodreads_file,"wb"),dialect='excel',quoting=csv.QUOTE_NONNUMERIC)
writer.writerows(target)

print "Done! saved output to " + goodreads_file
