#!/usr/bin/env python3
from pathlib import Path
import argparse, yaml, re

ap=argparse.ArgumentParser()
ap.add_argument('profile', nargs='?', default='config/search_profile.yml')
ap.add_argument('--allow-starter', action='store_true', help='Validate syntax but allow an unpersonalized starter profile')
args=ap.parse_args()
path=Path(args.profile)
profile=yaml.safe_load(path.read_text()) or {}
errors=[]
if not profile.get('role_rules'): errors.append('role_rules is empty')
if not profile.get('domain_rules'): errors.append('domain_rules is empty')
for section in ('role_rules','domain_rules','technical_rules','operating_model_rules','leadership_rules','seniority_rules'):
    for rule in profile.get(section,[]) or []:
        for pat in rule.get('patterns',[]) or []:
            try: re.compile(pat,re.I)
            except re.error as e: errors.append(f'{section}/{rule.get("name")}: invalid regex {pat!r}: {e}')
for section in ('penalty_rules',):
    for rule in profile.get(section,[]) or []:
        for key in ('title_patterns','text_patterns','unless_title_patterns','unless_text_patterns'):
            for pat in rule.get(key,[]) or []:
                try: re.compile(pat,re.I)
                except re.error as e: errors.append(f'{section}/{rule.get("name")}/{key}: invalid regex {pat!r}: {e}')
status=profile.get('profile_status','missing')
if status != 'personalized_ready' and not args.allow_starter:
    errors.append("profile_status is not 'personalized_ready'. Personalize config/search_profile.yml from your resume before production use.")
if errors:
    print('Profile validation FAILED:')
    for e in errors: print(' -',e)
    raise SystemExit(1)
print(f'Profile OK: {profile.get("profile_name","unnamed")}')
print('Status:',status)
print('Review threshold:',profile.get('score_bands',{}).get('review',65))
