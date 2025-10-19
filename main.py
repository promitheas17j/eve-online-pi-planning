#!/bin/env python3

import csv, glob, sys, json
from typing import Dict, List, Set

PLANET_RAW_MATERIALS: Dict[str, List[str]] = {
	"Barren": ["Aqueous Liquids", "Base Metals", "Carbon Compounds", "Microorganisms", "Noble Metals"],
	"Gas": ["Aqueous Liquids", "Base Metals", "Ionic Solutions", "Noble Gas", "Reactive Gas"],
	"Ice": ["Aqueous Liquids", "Heavy Metals", "Microorganisms", "Noble Gas", "Planktic Colonies"],
	"Lava": ["Base Metals", "Felsic Magma", "Heavy Metals", "Non-CS Crystals", "Suspended Plasma"],
	"Oceanic": ["Aqueous Liquids", "Carbon Compounds", "Complex Organisms", "Microorganisms", "Planktic Colonies"],
	"Plasma": ["Base Metals", "Heavy Metals", "Noble Metals", "Non-CS Crystals", "Suspended Plasma"],
	"Storm": ["Aqueous Liquids", "Base Metals", "Ionic Solutions", "Noble Gas", "Suspended Plasma"],
	"Temperate": ["Aqueous Liquids", "Autotrophs", "Carbon Compounds", "Complex Organisms", "Microorganisms"],
}

class SolarSystem:
	def __init__(self, constellation: str, name: str, planets: Dict[str, int]):
		self.constellation = constellation.strip()
		self.name = name.strip()
		self.planets = {ptype: count for ptype, count in planets.items() if count > 0}

	def get_available_materials(self) -> Set[str]:
		materials = set()
		for planet_type in self.planets:
			if planet_type in PLANET_RAW_MATERIALS:
				materials.update(PLANET_RAW_MATERIALS[planet_type])
		return materials

	def __str__(self):
		planet_summary = ', '.join(f"{ptype}({n})" for ptype, n in self.planets.items())
		return f"{self.name} ({self.constellation}): {planet_summary}"

def select_file():
	filename = ''
	files = []
	count = 1
	for file in glob.glob("*.csv"):
		print(f"{count}. {file}")
		files.append(file)
		count += 1
	print()
	choice = int(input("Select file to read (enter number of choice):"))
	if (choice < 1) or (choice > len(files)):
		print("Invalid choice. Exiting...")
		sys.exit()
	else:
		filename = files[choice - 1]
		return filename

def load_systems_from_csv(filepath: str) -> List[SolarSystem]:
	systems = []
	with open(filepath, newline='', encoding='utf-8-sig') as f:
		# reader = csv.DictReader(f, delimiter='\t')
		reader = csv.DictReader(f, delimiter=',')

		# Clean column names (strip whitespace and weird BOMs)
		reader.fieldnames = [name.strip() for name in reader.fieldnames]

		last_constellation = None
		for row in reader:
			# Strip keys/values
			row = {k.strip(): (v.strip() if v else '') for k, v in row.items()}

			# Some rows don't repeat constellation name → reuse last seen one
			constellation = row.get("Constellation", "")
			if constellation:
				last_constellation = constellation
			else:
				constellation = last_constellation or "Unknown"

			system_name = row.get("SolarSystem", "").strip()
			if not system_name:
				continue  # skip blank lines

			planet_counts = {}
			for planet_type in PLANET_RAW_MATERIALS.keys():
				val = row.get(planet_type, "")
				if val and val != "-":
					try:
						planet_counts[planet_type] = int(val)
					except ValueError:
						pass  # ignore malformed numbers

			systems.append(SolarSystem(constellation, system_name, planet_counts))
	return systems

def get_target_materials():
	all_materials = sorted({m for mats in PLANET_RAW_MATERIALS.values() for m in mats})
	target_materials = []
	while True:
		print("\n===============================")
		if target_materials:
			print("Currently selected materials:")
			for i, mat in enumerate(target_materials, 1):
				print(f"  {i}. {mat}")
		else:
			print("No raw materials selected yet.")
		print("\nAvailable materials:")
		available = [m for m in all_materials if m not in target_materials]
		for i, mat in enumerate(available, 1):
			print(f"  {i}. {mat}")
		print("\nOptions:")
		print("  A <number>  - Add material from available list")
		print("  R <number>  - Remove material from selected list")
		print("  D			 - Done / finish selection")
		print("===============================")
		choice = input("Enter command: ").strip().upper()
		if choice == "D":
			break
		elif choice.startswith("A "):
			try:
				idx = int(choice.split()[1]) - 1
				if 0 <= idx < len(available):
					mat = available[idx]
					target_materials.append(mat)
					print(f"Added: {mat}")
				else:
					print("Invalid number.")
			except ValueError:
				print("Invalid command format. Use e.g. 'A 2' to add.")
		elif choice.startswith("R "):
			try:
				idx = int(choice.split()[1]) - 1
				if 0 <= idx < len(target_materials):
					mat = target_materials.pop(idx)
					print(f"Removed: {mat}")
				else:
					print("Invalid number.")
			except ValueError:
				print("Invalid command format. Use e.g. 'R 1' to remove.")
		else:
			print("Unknown command. Use A, R, or D.")
	return target_materials

def find_systems_with_materials(systems: List[SolarSystem], desired_materials: List[str]) -> List[SolarSystem]:
	"""Return all systems that can produce ALL of the desired raw materials."""
	results = []
	desired = set(desired_materials)
	for system in systems:
		if desired.issubset(system.get_available_materials()):
			results.append(system)
	return results

def show_system_details(system: SolarSystem):
	print(f"\n{'='*40}")
	print(f"Solar System: {system.name}")
	print(f"Constellation: {system.constellation}")
	print(f"{'-'*40}")
	print(f"{'Planet Type':<20} {'Count':<6} {'Raw Materials'}")
	print(f"{'-'*40}")
	for planet_type, count in system.planets.items():
		materials = ", ".join(PLANET_RAW_MATERIALS.get(planet_type, []))
		print(f"{planet_type:<20} {count:<6} {materials}")

	print(f"{'='*40}\n")

def save_results_csv(matches: List[SolarSystem], filename: str):
	with open(filename, 'w', newline='') as f:
		writer = csv.writer(f)
		header = ["Constellation", "SolarSystem"] + list(PLANET_RAW_MATERIALS.keys())
		writer.writerow(header)
		for sys in matches:
			row = [sys.constellation, sys.name]
			for ptype in PLANET_RAW_MATERIALS.keys():
				row.append(sys.planets.get(ptype, 0))
			writer.writerow(row)
	print(f"Results saved to {filename}")

def save_query_state(csv_file: str, target_materials: List[str], filename: str):
	state = {"csv_file": csv_file, "target_materials": target_materials}
	with open(filename, "w") as f:
		json.dump(state, f)
	print(f"Query saved to {filename}")

def load_query_state(filename: str):
	with open(filename, "r") as f:
		state = json.load(f)
	return state["csv_file"], state["target_materials"]

if __name__ == "__main__":
	print("Do you want to load a previous query? (Y/N)")
	if input().strip().upper() == "Y":
		query_file = input("Enter query filename: ").strip()
		csv_file, target_materials = load_query_state(query_file)
		print(f"Loaded previous query: {csv_file} with materials {target_materials}")
	else:
		csv_file = select_file()
		target_materials = get_target_materials()
	systems = load_systems_from_csv(csv_file)
	matches = find_systems_with_materials(systems, target_materials)
	print(f"\nFound {len(matches)} systems matching {target_materials}:")
	if not matches:
		print("No matching systems found.")
	else:
		for i, system in enumerate(matches, 1):
			print(f"{i}. {system}")
		while True:
			choice = input("\nEnter system number for details (or 'Q' to quit, 'S' to save results, 'SQ' to save query): ").strip().upper()
			if choice == "Q":
				break
			elif choice == "S":
				outfile = input("Enter CSV filename to save results: ").strip()
				save_results_csv(matches, outfile)
			elif choice == "SQ":
				outfile = input("Enter filename to save query: ").strip()
				save_query_state(csv_file, target_materials, outfile)
			else:
				try:
					idx = int(choice) - 1
					if 0 <= idx < len(matches):
						show_system_details(matches[idx])
					else:
						print("Invalid number.")
				except ValueError:
					print("Invalid input. Please enter a number, 'Q', 'S', or 'SQ'.")

# if __name__ == "__main__":
# 	filename = select_file()
# 	systems = load_systems_from_csv(filename)
# 	target_materials = get_target_materials()
# 	matches = find_systems_with_materials(systems, target_materials)
# 	# print(f"Found {len(matches)} systems matching {target_materials}:")
# 	# for system in matches:
# 	# 	print(f" - {system}")
# 	print(f"\nFound {len(matches)} systems matching {target_materials}:")
# 	if not matches:
# 		print("No matching systems found.")
# 	else:
# 		for i, system in enumerate(matches, 1):
# 			print(f"{i}. {system}")
# 		while True:
# 			choice = input("\nEnter system number for details (or 'Q' to quit): ").strip().upper()
# 			if choice == "Q":
# 				break
# 			try:
# 				idx = int(choice) - 1
# 				if 0 <= idx < len(matches):
# 					show_system_details(matches[idx])
# 				else:
# 					print("Invalid number.")
# 			except ValueError:
# 				print("Invalid input. Please enter a number or 'Q'.")
