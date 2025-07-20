import os
import pickle

encodings_file = "/home/[Your_Name]/shared/seif/face_encodings.pkl"

def load_encodings(file_path):
    known_face_encodings = []
    known_face_names = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as f:
                known_face_encodings, known_face_names = pickle.load(f)
            print(f"Loaded {len(known_face_names)} existing faces.")
        except Exception as e:
            print(f"Error loading encodings file: {e}")
            print("Creating new empty lists for encodings.")
            known_face_encodings = []
            known_face_names = []
    else:
        print("Encodings file not found. Starting with empty list.")
    return known_face_encodings, known_face_names

def save_encodings(encodings, names, file_path):
    try:
        with open(file_path, 'wb') as f:
            pickle.dump((encodings, names), f)
        print(f"Encodings saved successfully. Total faces: {len(names)}.")
    except Exception as e:
        print(f"Error saving encodings file: {e}")

def delete_face():
    known_face_encodings, known_face_names = load_encodings(encodings_file)

    if not known_face_names:
        print("No faces currently saved to delete.")
        return

    print("\n--- Current Saved Faces ---")
    for i, name in enumerate(known_face_names):
        print(f"{i + 1}. {name}")
    print("--------------------------")

    while True:
        try:
            choice = input("Enter the number of the face to delete (or 'q' to quit): ").strip().lower()
            if choice == 'q':
                print("Exiting without deleting any faces.")
                break

            index_to_delete = int(choice) - 1

            if 0 <= index_to_delete < len(known_face_names):
                deleted_name = known_face_names.pop(index_to_delete)
                deleted_encoding = known_face_encodings.pop(index_to_delete)
                
                save_encodings(known_face_encodings, known_face_names, encodings_file)
                print(f"Successfully deleted '{deleted_name}'.")
                
         
                another_delete = input("Delete another face? (y/n): ").strip().lower()
                if another_delete != 'y':
                    break
                

                known_face_encodings, known_face_names = load_encodings(encodings_file)
                if not known_face_names: 
                    print("No more faces to delete.")
                    break
                print("\n--- Current Saved Faces After Deletion ---")
                for i, name in enumerate(known_face_names):
                    print(f"{i + 1}. {name}")
                print("------------------------------------------")

            else:
                print("Invalid number. Please enter a valid number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    delete_face()