import sys
from collections import defaultdict
from datetime import datetime

def parse_log_file(file_path):
    """
        Function to return the details in a file like user sessions
        the starting and ending time in the log.
    """
    user_sessions = defaultdict(list)
    first_session_time_in_file = None
    timestamp = None
    with open(file_path, 'r') as file:
        for i, line in enumerate(file,start=1):
            parts = line.strip().split()
            if len(parts) != 3:
                continue

            if parts[2] not in ['Start', 'End'] or (parts[1] and not parts[1].isalnum()):
                continue
            
            timestamp_str, user, action = parts
            if i == 1:
                first_session_time_in_file = datetime.strptime(timestamp_str, '%H:%M:%S')
            try:
                timestamp = datetime.strptime(timestamp_str, '%H:%M:%S')
                user_sessions[user].append((timestamp, action, False))
            except ValueError:
                pass
    return user_sessions, first_session_time_in_file, timestamp


def calculate_session_durations(user_sessions, first_session_time_in_file, last_session_time_in_file):
    """
        Function to calculate the sessions count and total duration of the sessions of a user.
    """
    results = []
    for user, sessions in user_sessions.items():
        sessions.sort()  # Sort sessions based on timestamp
        num_sessions = 0
        total_duration = 0
        for position, (timestamp, action, is_taken) in enumerate(sessions):
            if action == 'Start' and is_taken==False:
                start_time = timestamp
                sessions[position] = (timestamp, action, True)
                end_time = None
                for position, (timestamp, action, is_taken) in enumerate(sessions):
                    if action == 'End' and is_taken==False:
                        end_time = timestamp
                        session_duration = (end_time - start_time).seconds
                        total_duration += session_duration
                        sessions[position] = (timestamp, action, True)
                        break
                    if not end_time and position == (len(sessions) - 1):
                        end_time = last_session_time_in_file
                        session_duration = (end_time - start_time).seconds
                        total_duration += session_duration
                        sessions[position] = (timestamp, action, True)
                        break
                num_sessions += 1
            elif action == 'End' and is_taken==False:
                session_duration = (timestamp - first_session_time_in_file).seconds
                total_duration += session_duration
                num_sessions += 1
                sessions[position] = (timestamp, action, True)

        results.append((user, num_sessions, total_duration))

    return results


def main(file_path):
    user_sessions, first_session_time_in_file, last_session_time_in_file = parse_log_file(file_path)
    results = calculate_session_durations(user_sessions, first_session_time_in_file, last_session_time_in_file)

    print("Name   Sessions  Total Time")
    for user, num_sessions, total_duration in results:
        print(f"{user}   {num_sessions}         {total_duration}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python program_name.py <path_to_log_file>\n\nFor example,  python3 log_parser.py samplelog.txt")
        sys.exit(1)

    file_path = sys.argv[1]
    main(file_path)
