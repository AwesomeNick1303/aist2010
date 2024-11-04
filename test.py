import os, csv, re, json, random

genres = {}
metadata = {}
with open("harmonixset/dataset/metadata.csv") as file:
	reader = csv.DictReader(file)
	for line in reader:
		genre = line["Genre"]
		genres[genre] = genres.get(genre, 0)+1
		metadata[line["File"]] = line

allowed_genres = set([
	"Pop",
	"Country",
	"Rock"
])

def is_allowed_file(basefile):
	return (metadata[basefile]["Genre"] in allowed_genres) \
		and ("Ultra Dance" not in metadata[basefile]["Release"])

def get_all_segments():
	all_segments = {}
	fieldnames = ["boundary_time_stamp", "label"]
	dirname = "harmonixset/dataset/segments"
	segment_filenames = os.listdir(dirname)
	for filename in segment_filenames:
		basefile = os.path.splitext(filename)[0]
		if not is_allowed_file(basefile):
			continue
		with open(os.path.join(dirname, filename)) as file:
			reader = csv.DictReader(file, delimiter=" ", fieldnames=fieldnames)
			segments = list(reader)
			good_segments = True
			for section in segments:
				if section["label"] == "section":
					good_segments = False
			if good_segments:
				all_segments[basefile] = segments
	return all_segments


all_segments = get_all_segments()
types = set()
for file, segments in all_segments.items():
	for segment in segments:
		types.add(segment["label"])

merge_segments = {
	"altchorus": "chorus",
	"bigoutro": "outro",
	"bre": "break",
	"breakdown": "solo",
	"build": "transition",
	"chorus_instrumental": "instrumental",
	"chorushalf": "chorus",
	"chorusinst": "instrumental",
	"choruspart": "chorus",
	"drumroll": "instrumental",
	"fadein": "intro",
	"fast": "instrumental",
	"gtr": "solo",
	"gtrbreak": "solo",
	"guitar": "solo",
	"guitarsolo": "solo",
	"inst": "instrumental",
	"instbridge": "instrumental",
	"instchorus": "instrumental",
	"instintro": "intro",
	"instrumentalverse": "instrumental",
	"intchorus": "instrumental",
	"introchorus": "intro",
	"intropt": "intro",
	"introverse": "verse",
	"mainriff": "instrumental",
	"miniverse": "verse",
	"oddriff": "solo",
	"opening": "intro",
	"outroa": "outro",
	"postverse": "verse",
	"preverse": "verse",
	"quietchorus": "chorus",
	"raps": "verse",
	"refrain": "chorus",
	"rhythmlessintro": "intro",
	"saxobeat": "instrumental",
	"section": "unknown",
	"silence": "quiet",
	"slow": "instrumental",
	"slowverse": "verse",
	"stutter": "solo",
	"synth": "instrumental",
	"transitiona": "transition",
	"verse_slow": "verse",
	"versea": "verse",
	"verseinst": "instrumental",
	"versepart": "verse",
	"vocaloutro": "outro",
	"worstthingever": "instrumental"
}

def clean(label):
	label = re.sub(r'[0-9]+', '', label)
	label = merge_segments.get(label, label)
	return label

def get_clean_types():
	return list(set([clean(x) for x in types]))
def print_clean_types():
	print(get_clean_types())

def print_occurrances():
	occ = {}
	for file, segments in all_segments.items():
		for segment in segments:
			type = clean(segment["label"])
			occ[type] = occ.get(type, 0)+1
	print(occ)

print_clean_types()
print_occurrances()

def probs_from_prev2_occ():
	probs = {}
	for file, segments in all_segments.items():
		occ = {}
		prevprev = "none"
		prev = "start"
		for segment in segments:
			type = clean(segment["label"])

			twoprev = prevprev+","+prev
			occ[twoprev] = occ.get(twoprev, 0)+1
			twoprev = twoprev + " " + str(occ[twoprev])

			probs[twoprev] = probs.get(twoprev, {})
			probs[twoprev][type] = probs[twoprev].get(type, 0)+1

			prevprev = prev
			prev = type
			
	print(json.dumps(probs))

# probs_from_prev2_occ()

# determine next section by looking at how many times the last two sections have occurred
def probs_from_prev2_num_chorus():
	probs = {}
	for file, segments in all_segments.items():
		chorus = 0
		since_chorus = 0
		prevprev = "none"
		prev = "start"
		for segment in segments:
			type = clean(segment["label"])

			twoprev = prevprev+","+prev
			twoprev = twoprev + " " + str(chorus) + "," + str(since_chorus)

			probs[twoprev] = probs.get(twoprev, {})
			probs[twoprev][type] = probs[twoprev].get(type, 0)+1

			
			if type == "chorus" and prev != "chorus":
				chorus += 1
				since_chorus = 0
			else:
				since_chorus += 1

			prevprev = prev
			prev = type

	# print(json.dumps(probs))
	return probs

probs_from_prev2_num_chorus()

def generate_that(seed):
	random.seed(seed)
	probs = probs_from_prev2_num_chorus()

	chorus = 0
	since_chorus = 0
	prevprev = "none"
	prev = "start"
	output = []
	while prev != "end":
		twoprev = prevprev+","+prev
		twoprev = twoprev + " " + str(chorus) + "," + str(since_chorus)

		type = random.choices(list(probs[twoprev].keys()), weights=probs[twoprev].values())[0]

		if type == "chorus" and prev != "chorus":
			chorus += 1
			since_chorus = 0
		else:
			since_chorus += 1

		prevprev = prev
		prev = type

		output.append(type)
	
	return output

clean_types = get_clean_types()
minified_types = {}
for i in range(len(clean_types)):
	minified_types[clean_types[i]] = chr(ord('A')+i)
def minify(types):
	ret = ""
	for type in types:
		ret += minified_types[type]
	return ret

minified_dataset = {}
for file, segments in all_segments.items():
	types = []
	for segment in segments:
		types.append(clean(segment["label"]))
	minified_dataset[minify(types)] = file


for i in range(0, 100):
	types = generate_that(i)
	minified = minify(types)
	print(minified_dataset.get(minified, "nope"), minified, types)




# count_diff = {}
# pcfirst = 0
# npcfirst = 0
# for file, segments in all_segments.items():
# 	pc = 0
# 	npc = 0
# 	prev = "start"
# 	pcscore = 0
# 	npcscore = 0
# 	for segment in segments:
# 		type = segment["label"]
# 		if type == "chorus" and prev != "chorus":
# 			if prev == "prechorus":
# 				npcscore += npc
# 				pc += 1
# 			elif prev == "verse":
# 				pcscore += pc
# 				npc += 1
# 		prev = type
# 	pcfirst += pcscore
# 	npcfirst += npcscore

# print(pcfirst, npcfirst)