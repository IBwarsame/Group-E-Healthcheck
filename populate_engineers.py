import os
import django
import sys
import traceback # Import traceback for detailed error info

# --- !!! CONFIGURE YOUR PROJECT NAME HERE !!! ---
SETTINGS_MODULE = 'SEVENTYSEVENMARKS.settings'
# ---

# --- Configuration ---
NUM_ENGINEERS_PER_TEAM = 5
DEFAULT_PASSWORD = 'q'
MAX_ATTEMPTS_PER_ENGINEER = 3 # Safety break for persistent errors

# --- Setup Django Environment ---
print("--- Setting up Django environment ---")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_MODULE)
try:
    django.setup()
except ImportError as e:
    print(f"ERROR: Could not import Django or settings '{SETTINGS_MODULE}'.")
    print(f"Ensure Django is installed and '{SETTINGS_MODULE}' is correct.")
    print(f"Original error: {e}")
    sys.exit(1)
print("--- Django environment setup complete ---")

# --- Import Models (AFTER setup) ---
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction # Import transaction
# --- !!! UPDATE YOUR APP NAME HERE if it's not 'healthcheck' !!! ---
try:
    from healthcheck.models import UserProfile, Team, TeamMembership
except ImportError:
    print("ERROR: Could not import models from 'healthcheck'.")
    print("Make sure your app containing these models is named 'healthcheck' or update the import path.")
    sys.exit(1)
# ---

print(f"\n--- Starting Engineer Population ---")
print(f"Target: {NUM_ENGINEERS_PER_TEAM} engineers per team.")
print(f"Default password: '{DEFAULT_PASSWORD}' (CHANGE THIS!).")

engineer_counter = 1
total_engineers_created = 0
total_memberships_created = 0

teams = Team.objects.all()
if not teams.exists():
    print("\nWARNING: No teams found in the database. Exiting.")
    sys.exit(0)

print(f"\nFound {teams.count()} teams. Processing...")

for team in teams:
    print(f"\nProcessing Team: '{team.name}' (ID: {team.id})")
    engineers_added_to_this_team = 0
    consecutive_errors = 0 # Track errors for a specific engineer number

    while engineers_added_to_this_team < NUM_ENGINEERS_PER_TEAM:
        # --- Safety Break ---
        if consecutive_errors >= MAX_ATTEMPTS_PER_ENGINEER:
             print(f"  ERROR: Exceeded max attempts ({MAX_ATTEMPTS_PER_ENGINEER}) for engineer number near {engineer_counter}. Skipping rest for team '{team.name}'. Check logs.")
             break # Exit the inner while loop for this team

        username = f"eng{engineer_counter}"
        email_local_part = f"eng{engineer_counter}"
        email_domain = f"eng{engineer_counter}.com"
        email = f"{email_local_part}@{email_domain}"
        first_name = f"Eng{engineer_counter}"
        last_name = f"User"

        if User.objects.filter(username=username).exists():
            print(f"  Skipping: User '{username}' already exists. Incrementing counter.")
            engineer_counter += 1
            consecutive_errors = 0 # Reset error count for the new number
            continue

        try:
            # Use a transaction to ensure all related objects are created or none are
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=DEFAULT_PASSWORD,
                    first_name=first_name,
                    last_name=last_name
                )
                # If user creation succeeded, proceed
                UserProfile.objects.create(user=user, role='engineer')
                TeamMembership.objects.create(user=user, team=team)

            # If transaction succeeded:
            print(f"  + Created User: '{username}' (Email: {email})")
            total_engineers_created += 1
            print(f"    -> Added '{username}' to team '{team.name}'")
            total_memberships_created += 1

            engineers_added_to_this_team += 1 # Increment *only* on full success
            engineer_counter += 1             # Move to next engineer number
            consecutive_errors = 0            # Reset error count on success

        except IntegrityError as e:
            # This might happen if UserProfile or TeamMembership has unexpected unique constraints
            # or if the user check somehow failed (less likely)
            print(f"  ERROR: Database integrity error for '{username}'. Skipping.")
            print(f"    Details: {e}")
            # traceback.print_exc() # Uncomment for full traceback if needed
            engineer_counter += 1 # Try next engineer number
            consecutive_errors += 1 # Increment error count

        except Exception as e:
            # Catch any other error during creation
            print(f"  ERROR: An unexpected error occurred creating user '{username}' or related objects. Skipping.")
            print(f"    Details: {e}")
            print("-" * 20 + " Traceback " + "-" * 20)
            traceback.print_exc() # Print the full traceback to see where it fails
            print("-" * 50)
            engineer_counter += 1 # Try next engineer number
            consecutive_errors += 1 # Increment error count


    if engineers_added_to_this_team < NUM_ENGINEERS_PER_TEAM:
         print(f"  Warning: Only added {engineers_added_to_this_team}/{NUM_ENGINEERS_PER_TEAM} engineers to team '{team.name}' due to errors.")
    else:
        print(f"  Finished processing team '{team.name}'. Added {engineers_added_to_this_team} new engineers.")


print("\n--- Engineer Population Complete ---")
# ... (rest of the summary print statements) ...
