# ⚽ Football Data - Comprehensive Static Database

This directory contains comprehensive static football data for the FootyBot project with bilingual (Arabic/English) support.

## 📊 Data Overview

### 📁 Teams (`teams/` directory)
**30 league files | 816+ teams**

#### Major European Leagues
- `premier_league.json` - 20 teams (England)
- `la_liga.json` - 20 teams (Spain)
- `bundesliga.json` - 18 teams (Germany)
- `serie_a.json` - 20 teams (Italy)
- `ligue_1.json` - 18 teams (France)
- `eredivisie.json` - 18 teams (Netherlands)
- `portuguese_league.json` - 18 teams (Portugal)
- `belgian_league.json` - 18 teams (Belgium)
- `scottish_league.json` - 12 teams (Scotland)
- `turkish_league.json` - 20 teams (Turkey)

#### Second Divisions
- `championship.json` - 24 teams (England)
- `segunda_division.json` - 22 teams (Spain)
- `serie_b.json` - 20 teams (Italy)
- `ligue_2.json` - 20 teams (France)

#### Middle East & Africa
- `saudi_league.json` - 18 teams
- `egyptian_league.json` - 18 teams

#### Americas & Asia
- `mls.json` - 29 teams (USA)
- `brazilian_league.json` - 20 teams
- `argentine_league.json` - 28 teams
- `mexican_league.json` - 18 teams
- `japanese_league.json` - 18 teams
- `chinese_league.json` - 16 teams
- `australian_league.json` - 12 teams

#### International Competitions
- `champions_league.json` - 32 teams
- `europa_league.json` - 32 teams
- `world_cup_2022.json` - 32 national teams
- `afcon_2024.json` - 24 national teams
- `copa_america.json` - 16 national teams
- `asian_cup.json` - 24 national teams
- `international_teams.json` - 211 FIFA member nations

### 👥 Players (`players/` directory)
**18 files | 9,900+ players**

#### League-Specific Players
- `premier_league_players.json` - 500+ players
- `la_liga_players.json` - 500+ players
- `bundesliga_players.json` - 400+ players
- `serie_a_players.json` - 500+ players
- `ligue_1_players.json` - 400+ players
- `saudi_league_players.json` - 300+ players
- `egyptian_league_players.json` - 300+ players

#### Position-Based Categories
- `goalkeepers.json` - 500+ players
- `defenders.json` - 1,500+ players
- `midfielders.json` - 2,000+ players
- `forwards.json` - 1,500+ players

#### Regional Categories
- `african_players.json` - 500+ players
- `asian_players.json` - 500+ players
- `south_american_players.json` - 800+ players

#### Special Categories
- `international_stars.json` - 1,000+ top players
- `legends.json` - 500+ retired/veteran players
- `young_talents.json` - 500+ players under 23

#### Index
- `index.json` - Comprehensive player search index

### 🏟️ Leagues & Stadiums (`leagues/` directory)
**3 files**

- `leagues_info.json` - 127 leagues worldwide
- `competitions.json` - 30 international tournaments
- `stadiums.json` - 1,200+ stadiums

## 📋 Data Structure

### Team Format
```json
{
  "league": {
    "id": 39,
    "name": "Premier League",
    "name_ar": "الدوري الإنجليزي الممتاز",
    "country": "England",
    "country_ar": "إنجلترا",
    "season": "2024-2025"
  },
  "teams": [
    {
      "id": 33,
      "name": "Manchester United",
      "name_ar": "مانشستر يونايتد",
      "code": "MUN",
      "logo": "https://media.api-sports.io/football/teams/33.png",
      "founded": 1878,
      "stadium": {
        "name": "Old Trafford",
        "name_ar": "أولد ترافورد",
        "capacity": 76000,
        "city": "Manchester",
        "city_ar": "مانشستر"
      },
      "nickname": "Red Devils",
      "nickname_ar": "الشياطين الحمر",
      "colors": {
        "primary": "Red",
        "secondary": "White"
      },
      "trophies": {
        "league_titles": 20,
        "domestic_cups": 12,
        "european_cups": 3
      }
    }
  ]
}
```

### Player Format
```json
{
  "league": {
    "id": 39,
    "name": "Premier League",
    "name_ar": "الدوري الإنجليزي الممتاز"
  },
  "players": [
    {
      "id": 276,
      "name": "Mohamed Salah",
      "name_ar": "محمد صلاح",
      "age": 32,
      "birth": {
        "date": "1992-06-15",
        "place": "Nagrig",
        "place_ar": "نجريج",
        "country": "Egypt",
        "country_ar": "مصر"
      },
      "nationality": "Egypt",
      "nationality_ar": "مصري",
      "height": "175 cm",
      "weight": "71 kg",
      "photo": "https://media.api-sports.io/football/players/276.png",
      "current_team": {
        "id": 40,
        "name": "Liverpool",
        "name_ar": "ليفربول"
      },
      "position": "Forward",
      "position_ar": "مهاجم",
      "number": 11,
      "preferred_foot": "Left",
      "stats": {
        "appearances": 350,
        "goals": 210,
        "assists": 95,
        "yellow_cards": 18,
        "red_cards": 0
      },
      "market_value": "€65M",
      "contract_until": "2025-06-30"
    }
  ]
}
```

## 🔍 Usage Examples

### Load Team Data
```python
import json

# Load Premier League teams
with open('data/teams/premier_league.json', 'r', encoding='utf-8') as f:
    premier_league = json.load(f)
    
teams = premier_league['teams']
print(f"Total teams: {premier_league['total_teams']}")
```

### Load Player Data
```python
import json

# Load international stars
with open('data/players/international_stars.json', 'r', encoding='utf-8') as f:
    stars = json.load(f)
    
players = stars['players']
print(f"Total players: {stars['total_players']}")
```

### Search Players
```python
import json

# Load player index
with open('data/players/index.json', 'r', encoding='utf-8') as f:
    index = json.load(f)
    
# Find Mohamed Salah
player_info = index['search_index']['276']
print(f"Player: {player_info['name']} ({player_info['name_ar']})")
print(f"Team: {player_info['team']}")
print(f"File: {player_info['file']}")
```

## 🌐 Bilingual Support

All data includes:
- ✅ English names and information
- ✅ Arabic names and translations (العربية)
- ✅ Proper UTF-8 encoding
- ✅ RTL-compatible text

## 📝 Notes

- Data is static and can be used without API calls
- All team and player IDs match API-Football standard IDs where applicable
- Timestamps indicate last update time
- Data is formatted for easy parsing and querying
- Suitable for offline use and rapid prototyping

## 🔄 Updates

Last updated: 2024-12-15

To regenerate or update data, run:
```bash
python3 generate_players.py
python3 create_all_remaining_data.py
```

## 📄 License

This data is provided for use with the FootyBot project.

---

Made with ❤️ for football fans worldwide 🌍⚽
