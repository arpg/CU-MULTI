import rosbag
from datetime import datetime
import os

def split_rosbag_by_time(input_bag, output_dir, num_parts):
    # Open the input bag
    with rosbag.Bag(input_bag, 'r') as bag:
        start_time = bag.get_start_time()
        end_time = bag.get_end_time()
        total_duration = end_time - start_time

        # Calculate the time boundaries for the splits
        split_times = [start_time + i * total_duration / num_parts for i in range(1, num_parts)]

        print(f"Start time: {datetime.fromtimestamp(start_time)}")
        print(f"End time: {datetime.fromtimestamp(end_time)}")
        for i, split_time in enumerate(split_times, 1):
            print(f"Split {i} time: {datetime.fromtimestamp(split_time)}")

        # Open the output bags
        output_bags = []
        for i in range(num_parts):
            output_bag_name = os.path.join(output_dir, f'part_{i+1}.bag')
            output_bags.append(rosbag.Bag(output_bag_name, 'w'))

        try:
            for topic, msg, t in bag.read_messages():
                for i, split_time in enumerate(split_times):
                    if t.to_sec() < split_time:
                        output_bags[i].write(topic, msg, t)
                        break
                else:
                    output_bags[-1].write(topic, msg, t)
        finally:
            for bag in output_bags:
                bag.close()

    print(f"Bag split complete. {num_parts} parts saved in {output_dir}")

def merge_rosbags(input_bags, output_bag):
    # Open the output bag
    with rosbag.Bag(output_bag, 'w') as output_bag_handle:
        for input_bag in input_bags:
            with rosbag.Bag(input_bag, 'r') as bag:
                for topic, msg, t in bag.read_messages():
                    output_bag_handle.write(topic, msg, t)

    print(f"Bags {', '.join(input_bags)} merged into {output_bag}")

if __name__ == "__main__":
    input_bag = 'robot1_kittredge.bag'  # Replace with your input bag file name
    output_dir = './robot1_kittredge'  # Directory to save the split bag files
    num_parts = 2  # Number of parts to split the bag into

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    split_rosbag_by_time(input_bag, output_dir, num_parts)

    # Merging example
    merged_bag = 'robot3_main_new_merged.bag'
    input_bags = [os.path.join(output_dir, f'part_{i+1}.bag') for i in range(num_parts)]
    #merge_rosbags(input_bags, merged_bag)

