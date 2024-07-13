import os
import csv
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional


@dataclass
class Country_HQ:
    country_name: str
    country_code: str
    aliens: str
    predators: str
    dd_monsters: str

@dataclass
class Contacts:
    hq_name: str
    invader: str
    attack: str
    defense: str
    healing: str

@dataclass
class InvaderInfo:
    country_code: str
    invader_species: str
    role: str
    email: str


    @classmethod
    def create_invader_info(cls, country_hq_dict, contacts_dict):
        invader_info_list = []
        dd_monsters = ['d&d_beholder', 'd&d_devil', 'd&d_lich', 'd&d_mind_flayer', 'd&d_vampire', 'd&d_red_dragon', 'd&d_hill_giant', 'd&d_treant', 'd&d_werewolf', 'd&d_yuan-ti']

        def format_email(email):
            
            email = email.replace('capatain', 'captain')

            if email and not email.lower().endswith('.com'):
                return f"{email}@avengers.com"
            return email

        for country_data in country_hq_dict.values():
            country_code = country_data['country_code']
            
            # Process aliens and predators
            for invader_type in ['aliens', 'predators']:
                hq = country_data[invader_type]
                if hq in contacts_dict:
                    for contact in contacts_dict[hq]:
                        if contact.invader == invader_type:
                            for role in ['attack', 'defense', 'healing']:
                                email = getattr(contact, role)
                                if email:
                                    formatted_email = format_email(email)
                                    invader_info_list.append(cls(country_code, invader_type, f"{role}_role", formatted_email))

            # Process dd_monsters
            dd_hq = country_data['dd_monsters']
            if dd_hq in contacts_dict:
                for dd_monster in dd_monsters:
                    for contact in contacts_dict[dd_hq]:
                        if contact.invader == dd_monster:
                            for role in ['attack', 'defense', 'healing']:
                                email = getattr(contact, role)
                                if email:
                                    formatted_email = format_email(email)
                                    invader_info_list.append(cls(country_code, dd_monster, f"{role}_role", formatted_email))


        return invader_info_list

def create_invader_info_for_type(country_code: str, invader_type: str, contacts: List[Contacts]) -> List[InvaderInfo]:
    info_list = []
    for contact in contacts:
        if contact.attack:
            info_list.append(InvaderInfo(country_code, invader_type, 'attack_role', contact.attack))
        if contact.defense:
            info_list.append(InvaderInfo(country_code, invader_type, 'defense_role', contact.defense))
        if contact.healing:
            info_list.append(InvaderInfo(country_code, invader_type, 'healing_role', contact.healing))
    return info_list

def parse_contacts_from_file(file_path: str) -> List[Contacts]:
    contacts = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        hq_name = lines[0].split('\t')[0].strip()
        
        for line in lines[1:]:
            parts = line.strip().split('\t')
            contact = Contacts(
                hq_name=hq_name,
                invader=parts[0],
                attack=parts[1] if len(parts) > 1 else '',
                defense=parts[2] if len(parts) > 2 else '',
                healing=parts[3] if len(parts) > 3 else ''
            )
            contacts.append(contact)
    return contacts

def gather_all_contacts(folder_path: str) -> Dict[str, List[Contacts]]:
    all_contacts = {}
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            contacts = parse_contacts_from_file(file_path)
            
            # Use the filename (without extension) as the key
            key = os.path.splitext(filename)[0]
            all_contacts[key] = contacts
    
    return all_contacts


class TextDataExtractor:
    @staticmethod
    def extract_members_to_dict(file_path):
        country_hq_dict = {}
        
        with open(file_path, 'r') as file:
            next(file)  # Skip the header line if it exists
            for line in file:
                fields = line.strip().split('\t')
                if len(fields) >= 5:
                    country_name = fields[0].strip()
                    country_hq_dict[country_name] = {
                        'country_code': fields[1].strip(),
                        'aliens': fields[2].strip(),
                        'predators': fields[3].strip(),
                        'dd_monsters': fields[4].strip()
                    }
        
        return country_hq_dict


def write_invader_info_to_csv(file_path: str, invader_info_list: List[InvaderInfo]):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Country_Code', 'Invader_Species', 'Role', 'Email']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for info in invader_info_list:
            writer.writerow({
                'Country_Code': info.country_code,
                'Invader_Species': info.invader_species,
                'Role': info.role,
                'Email': info.email
            })

def create_email_specific_csv(invader_info_list, contacts_dist, email, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    
    # Get the main part of the email (without @avengers.com)
    email_main = email.split('@')[0]
    
    # Create a valid filename from the email
    #valid_filename = "".join(c for c in email_main if c.isalnum() or c in (' ', '.', '_')).rstrip()
    #output_file_path = os.path.join(output_folder, f"{valid_filename}.csv")
    
    # Define the HQ names and invader species
    hq_list = []
    
    for item in contacts_dist:
        child = contacts_dist[item]
        print(type(child[:]))
        hq_list.append(child)
    print(len(hq_list))
    
    

if __name__ == "__main__":
    country_hq_file_path = "Option2_Tab_Delimited_Text/country_hq.txt"
    extractor = TextDataExtractor()
    country_hq_dict = extractor.extract_members_to_dict(country_hq_file_path)

    contacts_folder_path = "Option2_Tab_Delimited_Text/contacts"
    all_contacts = gather_all_contacts(contacts_folder_path)

    #print(f"\nTotal files processed: {len(all_contacts)}")

    invader_info_list = InvaderInfo.create_invader_info(country_hq_dict, all_contacts)

    # Check if we have 12 invader species for each country
    country_invader_count = {}
    for info in invader_info_list:
        if info.country_code not in country_invader_count:
            country_invader_count[info.country_code] = set()
        country_invader_count[info.country_code].add(info.invader_species)

    #for country, invaders in country_invader_count.items():
    #    if len(invaders) != 12:
    #        print(f"Warning: Country {country} has {len(invaders)} invader species instead of 12")

    # Print the results and check emails
    '''
    for info in invader_info_list:
        print(info)
        if not info.email.lower().endswith('.com'):
            print(f"Warning: Email for {info.country_code}, {info.invader_species}, {info.role} does not end with .com")
    '''
    output_file_path = "invader_info.csv"
    write_invader_info_to_csv(output_file_path, invader_info_list)

    print(f"Invader info has been written to {output_file_path}")


    #################################TASK 2##########################################################################
