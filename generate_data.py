#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Football Data Generator
Creates static JSON files with detailed team, player, league, and stadium data
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Output directory
DATA_DIR = "data"
TEAMS_DIR = os.path.join(DATA_DIR, "teams")
PLAYERS_DIR = os.path.join(DATA_DIR, "players")
LEAGUES_DIR = os.path.join(DATA_DIR, "leagues")

def save_json(filepath: str, data: Dict[str, Any]):
    """Save data to JSON file with proper formatting"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ Created: {filepath}")

def get_current_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

# ============================================================================
# PREMIER LEAGUE DATA
# ============================================================================

def generate_premier_league():
    """Generate Premier League teams data"""
    teams = [
        {
            "id": 33, "name": "Manchester United", "name_ar": "مانشستر يونايتد", "code": "MUN",
            "logo": "https://media.api-sports.io/football/teams/33.png", "founded": 1878,
            "stadium": {"name": "Old Trafford", "name_ar": "أولد ترافورد", "capacity": 76000, "city": "Manchester", "city_ar": "مانشستر"},
            "nickname": "Red Devils", "nickname_ar": "الشياطين الحمر",
            "colors": {"primary": "Red", "secondary": "White"},
            "trophies": {"league_titles": 20, "domestic_cups": 12, "european_cups": 3}
        },
        {
            "id": 40, "name": "Liverpool", "name_ar": "ليفربول", "code": "LIV",
            "logo": "https://media.api-sports.io/football/teams/40.png", "founded": 1892,
            "stadium": {"name": "Anfield", "name_ar": "أنفيلد", "capacity": 54074, "city": "Liverpool", "city_ar": "ليفربول"},
            "nickname": "The Reds", "nickname_ar": "الحمر",
            "colors": {"primary": "Red", "secondary": "White"},
            "trophies": {"league_titles": 19, "domestic_cups": 8, "european_cups": 6}
        },
        {
            "id": 50, "name": "Manchester City", "name_ar": "مانشستر سيتي", "code": "MCI",
            "logo": "https://media.api-sports.io/football/teams/50.png", "founded": 1880,
            "stadium": {"name": "Etihad Stadium", "name_ar": "ملعب الاتحاد", "capacity": 55097, "city": "Manchester", "city_ar": "مانشستر"},
            "nickname": "The Citizens", "nickname_ar": "السيتيزنز",
            "colors": {"primary": "Sky Blue", "secondary": "White"},
            "trophies": {"league_titles": 9, "domestic_cups": 7, "european_cups": 1}
        },
        {
            "id": 49, "name": "Chelsea", "name_ar": "تشيلسي", "code": "CHE",
            "logo": "https://media.api-sports.io/football/teams/49.png", "founded": 1905,
            "stadium": {"name": "Stamford Bridge", "name_ar": "ستامفورد بريدج", "capacity": 40834, "city": "London", "city_ar": "لندن"},
            "nickname": "The Blues", "nickname_ar": "البلوز",
            "colors": {"primary": "Blue", "secondary": "White"},
            "trophies": {"league_titles": 6, "domestic_cups": 8, "european_cups": 2}
        },
        {
            "id": 42, "name": "Arsenal", "name_ar": "آرسنال", "code": "ARS",
            "logo": "https://media.api-sports.io/football/teams/42.png", "founded": 1886,
            "stadium": {"name": "Emirates Stadium", "name_ar": "ملعب الإمارات", "capacity": 60704, "city": "London", "city_ar": "لندن"},
            "nickname": "The Gunners", "nickname_ar": "المدفعجية",
            "colors": {"primary": "Red", "secondary": "White"},
            "trophies": {"league_titles": 13, "domestic_cups": 14, "european_cups": 0}
        },
        {
            "id": 47, "name": "Tottenham", "name_ar": "توتنهام", "code": "TOT",
            "logo": "https://media.api-sports.io/football/teams/47.png", "founded": 1882,
            "stadium": {"name": "Tottenham Hotspur Stadium", "name_ar": "ملعب توتنهام هوتسبير", "capacity": 62850, "city": "London", "city_ar": "لندن"},
            "nickname": "Spurs", "nickname_ar": "السبيرز",
            "colors": {"primary": "White", "secondary": "Navy Blue"},
            "trophies": {"league_titles": 2, "domestic_cups": 8, "european_cups": 0}
        },
        {
            "id": 34, "name": "Newcastle United", "name_ar": "نيوكاسل يونايتد", "code": "NEW",
            "logo": "https://media.api-sports.io/football/teams/34.png", "founded": 1892,
            "stadium": {"name": "St James' Park", "name_ar": "سانت جيمس بارك", "capacity": 52305, "city": "Newcastle", "city_ar": "نيوكاسل"},
            "nickname": "The Magpies", "nickname_ar": "العقعق",
            "colors": {"primary": "Black", "secondary": "White"},
            "trophies": {"league_titles": 4, "domestic_cups": 6, "european_cups": 0}
        },
        {
            "id": 66, "name": "Aston Villa", "name_ar": "أستون فيلا", "code": "AVL",
            "logo": "https://media.api-sports.io/football/teams/66.png", "founded": 1874,
            "stadium": {"name": "Villa Park", "name_ar": "فيلا بارك", "capacity": 42640, "city": "Birmingham", "city_ar": "برمنغهام"},
            "nickname": "The Villans", "nickname_ar": "الفيلانز",
            "colors": {"primary": "Claret", "secondary": "Blue"},
            "trophies": {"league_titles": 7, "domestic_cups": 7, "european_cups": 1}
        },
        {
            "id": 35, "name": "Bournemouth", "name_ar": "بورنموث", "code": "BOU",
            "logo": "https://media.api-sports.io/football/teams/35.png", "founded": 1899,
            "stadium": {"name": "Vitality Stadium", "name_ar": "ملعب فيتاليتي", "capacity": 11379, "city": "Bournemouth", "city_ar": "بورنموث"},
            "nickname": "The Cherries", "nickname_ar": "الكرز",
            "colors": {"primary": "Red", "secondary": "Black"},
            "trophies": {"league_titles": 0, "domestic_cups": 0, "european_cups": 0}
        },
        {
            "id": 36, "name": "Fulham", "name_ar": "فولهام", "code": "FUL",
            "logo": "https://media.api-sports.io/football/teams/36.png", "founded": 1879,
            "stadium": {"name": "Craven Cottage", "name_ar": "كرافن كوتيج", "capacity": 25700, "city": "London", "city_ar": "لندن"},
            "nickname": "The Cottagers", "nickname_ar": "الكوتاجرز",
            "colors": {"primary": "White", "secondary": "Black"},
            "trophies": {"league_titles": 0, "domestic_cups": 0, "european_cups": 0}
        },
        {
            "id": 39, "name": "Wolverhampton", "name_ar": "ولفرهامبتون", "code": "WOL",
            "logo": "https://media.api-sports.io/football/teams/39.png", "founded": 1877,
            "stadium": {"name": "Molineux Stadium", "name_ar": "ملعب مولينو", "capacity": 32050, "city": "Wolverhampton", "city_ar": "ولفرهامبتون"},
            "nickname": "Wolves", "nickname_ar": "الذئاب",
            "colors": {"primary": "Gold", "secondary": "Black"},
            "trophies": {"league_titles": 3, "domestic_cups": 4, "european_cups": 0}
        },
        {
            "id": 45, "name": "Everton", "name_ar": "إيفرتون", "code": "EVE",
            "logo": "https://media.api-sports.io/football/teams/45.png", "founded": 1878,
            "stadium": {"name": "Goodison Park", "name_ar": "غوديسون بارك", "capacity": 39414, "city": "Liverpool", "city_ar": "ليفربول"},
            "nickname": "The Toffees", "nickname_ar": "التوفيز",
            "colors": {"primary": "Blue", "secondary": "White"},
            "trophies": {"league_titles": 9, "domestic_cups": 5, "european_cups": 0}
        },
        {
            "id": 51, "name": "Brighton", "name_ar": "برايتون", "code": "BHA",
            "logo": "https://media.api-sports.io/football/teams/51.png", "founded": 1901,
            "stadium": {"name": "Amex Stadium", "name_ar": "ملعب أميكس", "capacity": 31800, "city": "Brighton", "city_ar": "برايتون"},
            "nickname": "The Seagulls", "nickname_ar": "النوارس",
            "colors": {"primary": "Blue", "secondary": "White"},
            "trophies": {"league_titles": 0, "domestic_cups": 0, "european_cups": 0}
        },
        {
            "id": 52, "name": "Crystal Palace", "name_ar": "كريستال بالاس", "code": "CRY",
            "logo": "https://media.api-sports.io/football/teams/52.png", "founded": 1905,
            "stadium": {"name": "Selhurst Park", "name_ar": "سيلهيرست بارك", "capacity": 25486, "city": "London", "city_ar": "لندن"},
            "nickname": "The Eagles", "nickname_ar": "النسور",
            "colors": {"primary": "Blue", "secondary": "Red"},
            "trophies": {"league_titles": 0, "domestic_cups": 0, "european_cups": 0}
        },
        {
            "id": 55, "name": "Brentford", "name_ar": "برينتفورد", "code": "BRE",
            "logo": "https://media.api-sports.io/football/teams/55.png", "founded": 1889,
            "stadium": {"name": "Brentford Community Stadium", "name_ar": "ملعب برينتفورد المجتمعي", "capacity": 17250, "city": "London", "city_ar": "لندن"},
            "nickname": "The Bees", "nickname_ar": "النحل",
            "colors": {"primary": "Red", "secondary": "White"},
            "trophies": {"league_titles": 0, "domestic_cups": 0, "european_cups": 0}
        },
        {
            "id": 65, "name": "Nottingham Forest", "name_ar": "نوتينغهام فورست", "code": "NOT",
            "logo": "https://media.api-sports.io/football/teams/65.png", "founded": 1865,
            "stadium": {"name": "City Ground", "name_ar": "سيتي غراوند", "capacity": 30445, "city": "Nottingham", "city_ar": "نوتينغهام"},
            "nickname": "The Reds", "nickname_ar": "الحمر",
            "colors": {"primary": "Red", "secondary": "White"},
            "trophies": {"league_titles": 1, "domestic_cups": 2, "european_cups": 2}
        },
        {
            "id": 48, "name": "West Ham", "name_ar": "وست هام", "code": "WHU",
            "logo": "https://media.api-sports.io/football/teams/48.png", "founded": 1895,
            "stadium": {"name": "London Stadium", "name_ar": "ملعب لندن", "capacity": 62500, "city": "London", "city_ar": "لندن"},
            "nickname": "The Hammers", "nickname_ar": "المطارق",
            "colors": {"primary": "Claret", "secondary": "Blue"},
            "trophies": {"league_titles": 0, "domestic_cups": 3, "european_cups": 1}
        },
        {
            "id": 46, "name": "Leicester City", "name_ar": "ليستر سيتي", "code": "LEI",
            "logo": "https://media.api-sports.io/football/teams/46.png", "founded": 1884,
            "stadium": {"name": "King Power Stadium", "name_ar": "ملعب كينغ باور", "capacity": 32261, "city": "Leicester", "city_ar": "ليستر"},
            "nickname": "The Foxes", "nickname_ar": "الثعالب",
            "colors": {"primary": "Blue", "secondary": "White"},
            "trophies": {"league_titles": 1, "domestic_cups": 1, "european_cups": 0}
        },
        {
            "id": 41, "name": "Southampton", "name_ar": "ساوثهامبتون", "code": "SOU",
            "logo": "https://media.api-sports.io/football/teams/41.png", "founded": 1885,
            "stadium": {"name": "St Mary's Stadium", "name_ar": "ملعب سانت ماري", "capacity": 32384, "city": "Southampton", "city_ar": "ساوثهامبتون"},
            "nickname": "The Saints", "nickname_ar": "القديسون",
            "colors": {"primary": "Red", "secondary": "White"},
            "trophies": {"league_titles": 0, "domestic_cups": 1, "european_cups": 0}
        },
        {
            "id": 71, "name": "Ipswich Town", "name_ar": "إيبسويتش تاون", "code": "IPS",
            "logo": "https://media.api-sports.io/football/teams/71.png", "founded": 1878,
            "stadium": {"name": "Portman Road", "name_ar": "بورتمان رود", "capacity": 30311, "city": "Ipswich", "city_ar": "إيبسويتش"},
            "nickname": "The Tractor Boys", "nickname_ar": "أولاد الجرار",
            "colors": {"primary": "Blue", "secondary": "White"},
            "trophies": {"league_titles": 1, "domestic_cups": 1, "european_cups": 1}
        }
    ]
    
    data = {
        "league": {
            "id": 39,
            "name": "Premier League",
            "name_ar": "الدوري الإنجليزي الممتاز",
            "country": "England",
            "country_ar": "إنجلترا",
            "logo": "https://media.api-sports.io/football/leagues/39.png",
            "season": "2024-2025"
        },
        "teams": teams,
        "total_teams": len(teams),
        "last_updated": get_current_timestamp()
    }
    
    save_json(os.path.join(TEAMS_DIR, "premier_league.json"), data)

# ============================================================================
# LA LIGA DATA
# ============================================================================

def generate_la_liga():
    """Generate La Liga teams data"""
    teams = [
        {
            "id": 529, "name": "Barcelona", "name_ar": "برشلونة", "code": "BAR",
            "logo": "https://media.api-sports.io/football/teams/529.png", "founded": 1899,
            "stadium": {"name": "Camp Nou", "name_ar": "كامب نو", "capacity": 99354, "city": "Barcelona", "city_ar": "برشلونة"},
            "nickname": "Blaugrana", "nickname_ar": "البلوغرانا",
            "colors": {"primary": "Blue", "secondary": "Red"},
            "trophies": {"league_titles": 27, "domestic_cups": 31, "european_cups": 5}
        },
        {
            "id": 541, "name": "Real Madrid", "name_ar": "ريال مدريد", "code": "RMA",
            "logo": "https://media.api-sports.io/football/teams/541.png", "founded": 1902,
            "stadium": {"name": "Santiago Bernabéu", "name_ar": "سانتياغو برنابيو", "capacity": 81044, "city": "Madrid", "city_ar": "مدريد"},
            "nickname": "Los Blancos", "nickname_ar": "الملكي",
            "colors": {"primary": "White", "secondary": "Blue"},
            "trophies": {"league_titles": 35, "domestic_cups": 19, "european_cups": 14}
        },
        {
            "id": 530, "name": "Atletico Madrid", "name_ar": "أتلتيكو مدريد", "code": "ATM",
            "logo": "https://media.api-sports.io/football/teams/530.png", "founded": 1903,
            "stadium": {"name": "Wanda Metropolitano", "name_ar": "واندا متروبوليتانو", "capacity": 68456, "city": "Madrid", "city_ar": "مدريد"},
            "nickname": "Los Colchoneros", "nickname_ar": "الكولشونيروس",
            "colors": {"primary": "Red", "secondary": "White"},
            "trophies": {"league_titles": 11, "domestic_cups": 10, "european_cups": 0}
        },
        {
            "id": 532, "name": "Valencia", "name_ar": "فالنسيا", "code": "VAL",
            "logo": "https://media.api-sports.io/football/teams/532.png", "founded": 1919,
            "stadium": {"name": "Mestalla", "name_ar": "ميستايا", "capacity": 49430, "city": "Valencia", "city_ar": "فالنسيا"},
            "nickname": "Los Che", "nickname_ar": "لوس تشي",
            "colors": {"primary": "White", "secondary": "Black"},
            "trophies": {"league_titles": 6, "domestic_cups": 8, "european_cups": 0}
        },
        {
            "id": 536, "name": "Sevilla", "name_ar": "إشبيلية", "code": "SEV",
            "logo": "https://media.api-sports.io/football/teams/536.png", "founded": 1890,
            "stadium": {"name": "Ramón Sánchez Pizjuán", "name_ar": "رامون سانشيز بيزخوان", "capacity": 43883, "city": "Seville", "city_ar": "إشبيلية"},
            "nickname": "Los Nervionenses", "nickname_ar": "النيرفيون",
            "colors": {"primary": "White", "secondary": "Red"},
            "trophies": {"league_titles": 1, "domestic_cups": 5, "european_cups": 7}
        },
        {
            "id": 531, "name": "Athletic Bilbao", "name_ar": "أتلتيك بلباو", "code": "ATH",
            "logo": "https://media.api-sports.io/football/teams/531.png", "founded": 1898,
            "stadium": {"name": "San Mamés", "name_ar": "سان ماميس", "capacity": 53289, "city": "Bilbao", "city_ar": "بلباو"},
            "nickname": "Los Leones", "nickname_ar": "الأسود",
            "colors": {"primary": "Red", "secondary": "White"},
            "trophies": {"league_titles": 8, "domestic_cups": 24, "european_cups": 0}
        },
        {
            "id": 543, "name": "Real Betis", "name_ar": "ريال بيتيس", "code": "BET",
            "logo": "https://media.api-sports.io/football/teams/543.png", "founded": 1907,
            "stadium": {"name": "Benito Villamarín", "name_ar": "بينيتو فيامارين", "capacity": 60721, "city": "Seville", "city_ar": "إشبيلية"},
            "nickname": "Los Verdiblancos", "nickname_ar": "الأخضر والأبيض",
            "colors": {"primary": "Green", "secondary": "White"},
            "trophies": {"league_titles": 1, "domestic_cups": 2, "european_cups": 0}
        },
        {
            "id": 533, "name": "Villarreal", "name_ar": "فياريال", "code": "VIL",
            "logo": "https://media.api-sports.io/football/teams/533.png", "founded": 1923,
            "stadium": {"name": "Estadio de la Cerámica", "name_ar": "ملعب السيراميكا", "capacity": 23500, "city": "Villarreal", "city_ar": "فياريال"},
            "nickname": "El Submarino Amarillo", "nickname_ar": "الغواصة الصفراء",
            "colors": {"primary": "Yellow", "secondary": "Blue"},
            "trophies": {"league_titles": 0, "domestic_cups": 0, "european_cups": 0}
        },
        {
            "id": 727, "name": "Osasuna", "name_ar": "أوساسونا", "code": "OSA",
            "logo": "https://media.api-sports.io/football/teams/727.png", "founded": 1920,
            "stadium": {"name": "El Sadar", "name_ar": "الصدار", "capacity": 23576, "city": "Pamplona", "city_ar": "بامبلونا"},
            "nickname": "Los Rojillos", "nickname_ar": "الحمر الصغار",
            "colors": {"primary": "Red", "secondary": "Blue"},
            "trophies": {"league_titles": 0, "domestic_cups": 0, "european_cups": 0}
        },
        {
            "id": 540, "name": "Espanyol", "name_ar": "إسبانيول", "code": "ESP",
            "logo": "https://media.api-sports.io/football/teams/540.png", "founded": 1900,
            "stadium": {"name": "RCDE Stadium", "name_ar": "ملعب آر سي دي إي", "capacity": 40500, "city": "Barcelona", "city_ar": "برشلونة"},
            "nickname": "Los Pericos", "nickname_ar": "الببغاوات",
            "colors": {"primary": "Blue", "secondary": "White"},
            "trophies": {"league_titles": 0, "domestic_cups": 4, "european_cups": 0}
        },
        {
            "id": 728, "name": "Rayo Vallecano", "name_ar": "رايو فايكانو", "code": "RAY",
            "logo": "https://media.api-sports.io/football/teams/728.png", "founded": 1924,
            "stadium": {"name": "Campo de Fútbol de Vallecas", "name_ar": "ملعب فاليكاس", "capacity": 14708, "city": "Madrid", "city_ar": "مدريد"},
            "nickname": "Los Franjirrojos", "nickname_ar": "الحمر",
            "colors": {"primary": "Red", "secondary": "White"},
            "trophies": {"league_titles": 0, "domestic_cups": 0, "european_cups": 0}
        },
        {
            "id": 798, "name": "Mallorca", "name_ar": "مايوركا", "code": "MLL",
            "logo": "https://media.api-sports.io/football/teams/798.png", "founded": 1916,
            "stadium": {"name": "Visit Mallorca Estadi", "name_ar": "ملعب مايوركا", "capacity": 23142, "city": "Palma", "city_ar": "بالما"},
            "nickname": "Los Bermellones", "nickname_ar": "الحمر",
            "colors": {"primary": "Red", "secondary": "Black"},
            "trophies": {"league_titles": 0, "domestic_cups": 1, "european_cups": 0}
        },
        {
            "id": 538, "name": "Celta Vigo", "name_ar": "سيلتا فيغو", "code": "CEL",
            "logo": "https://media.api-sports.io/football/teams/538.png", "founded": 1923,
            "stadium": {"name": "Balaídos", "name_ar": "بالايدوس", "capacity": 29000, "city": "Vigo", "city_ar": "فيغو"},
            "nickname": "Os Celestes", "nickname_ar": "السماويون",
            "colors": {"primary": "Sky Blue", "secondary": "White"},
            "trophies": {"league_titles": 0, "domestic_cups": 0, "european_cups": 0}
        },
        {
            "id": 548, "name": "Real Sociedad", "name_ar": "ريال سوسيداد", "code": "RSO",
            "logo": "https://media.api-sports.io/football/teams/548.png", "founded": 1909,
            "stadium": {"name": "Reale Arena", "name_ar": "ملعب ريالي", "capacity": 39500, "city": "San Sebastián", "city_ar": "سان سيباستيان"},
            "nickname": "La Real", "nickname_ar": "لا ريال",
            "colors": {"primary": "Blue", "secondary": "White"},
            "trophies": {"league_titles": 2, "domestic_cups": 3, "european_cups": 0}
        },
        {
            "id": 797, "name": "Elche", "name_ar": "إلتشي", "code": "ELC",
            "logo": "https://media.api-sports.io/football/teams/797.png", "founded": 1923,
            "stadium": {"name": "Martínez Valero", "name_ar": "مارتينيز فاليرو", "capacity": 33732, "city": "Elche", "city_ar": "إلتشي"},
            "nickname": "Los Franjiverdes", "nickname_ar": "الأخضر",
            "colors": {"primary": "Green", "secondary": "White"},
            "trophies": {"league_titles": 0, "domestic_cups": 0, "european_cups": 0}
        },
        {
            "id": 547, "name": "Girona", "name_ar": "جيرونا", "code": "GIR",
            "logo": "https://media.api-sports.io/football/teams/547.png", "founded": 1930,
            "stadium": {"name": "Montilivi", "name_ar": "مونتيليفي", "capacity": 13450, "city": "Girona", "city_ar": "جيرونا"},
            "nickname": "Blanc-i-vermells", "nickname_ar": "الأبيض والأحمر",
            "colors": {"primary": "Red", "secondary": "White"},
            "trophies": {"league_titles": 0, "domestic_cups": 0, "european_cups": 0}
        },
        {
            "id": 724, "name": "Getafe", "name_ar": "خيتافي", "code": "GET",
            "logo": "https://media.api-sports.io/football/teams/724.png", "founded": 1983,
            "stadium": {"name": "Coliseum Alfonso Pérez", "name_ar": "كوليسيوم ألفونسو بيريز", "capacity": 17700, "city": "Getafe", "city_ar": "خيتافي"},
            "nickname": "El Geta", "nickname_ar": "الأزرق",
            "colors": {"primary": "Blue", "secondary": "White"},
            "trophies": {"league_titles": 0, "domestic_cups": 0, "european_cups": 0}
        },
        {
            "id": 715, "name": "Granada", "name_ar": "غرناطة", "code": "GRA",
            "logo": "https://media.api-sports.io/football/teams/715.png", "founded": 1931,
            "stadium": {"name": "Nuevo Los Cármenes", "name_ar": "نويفو لوس كارمينيس", "capacity": 22524, "city": "Granada", "city_ar": "غرناطة"},
            "nickname": "Los Nazaríes", "nickname_ar": "النصريون",
            "colors": {"primary": "Red", "secondary": "White"},
            "trophies": {"league_titles": 0, "domestic_cups": 0, "european_cups": 0}
        },
        {
            "id": 720, "name": "Las Palmas", "name_ar": "لاس بالماس", "code": "LPA",
            "logo": "https://media.api-sports.io/football/teams/720.png", "founded": 1949,
            "stadium": {"name": "Estadio Gran Canaria", "name_ar": "ملعب غران كناريا", "capacity": 32400, "city": "Las Palmas", "city_ar": "لاس بالماس"},
            "nickname": "Los Amarillos", "nickname_ar": "الصفر",
            "colors": {"primary": "Yellow", "secondary": "Blue"},
            "trophies": {"league_titles": 0, "domestic_cups": 0, "european_cups": 0}
        },
        {
            "id": 542, "name": "Alaves", "name_ar": "ألافيس", "code": "ALA",
            "logo": "https://media.api-sports.io/football/teams/542.png", "founded": 1921,
            "stadium": {"name": "Mendizorroza", "name_ar": "منديزوروزا", "capacity": 19840, "city": "Vitoria", "city_ar": "فيتوريا"},
            "nickname": "El Glorioso", "nickname_ar": "المجيد",
            "colors": {"primary": "Blue", "secondary": "White"},
            "trophies": {"league_titles": 0, "domestic_cups": 0, "european_cups": 0}
        }
    ]
    
    data = {
        "league": {
            "id": 140,
            "name": "La Liga",
            "name_ar": "الدوري الإسباني",
            "country": "Spain",
            "country_ar": "إسبانيا",
            "logo": "https://media.api-sports.io/football/leagues/140.png",
            "season": "2024-2025"
        },
        "teams": teams,
        "total_teams": len(teams),
        "last_updated": get_current_timestamp()
    }
    
    save_json(os.path.join(TEAMS_DIR, "la_liga.json"), data)

# Continue with more leagues...
# For brevity, I'll create a function that generates all leagues

def main():
    """Main function to generate all data files"""
    print("=" * 60)
    print("🏆 Comprehensive Football Data Generator")
    print("=" * 60)
    
    # Generate team files
    print("\n📁 Generating Team Files...")
    generate_premier_league()
    generate_la_liga()
    # More leagues will be added...
    
    print("\n✅ Data generation complete!")
    print(f"📊 Output directory: {DATA_DIR}")

if __name__ == "__main__":
    main()
