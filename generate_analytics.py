import pandas as pd
import matplotlib.pyplot as plt

print("Analyzing RecycloVision Telemetry Data...")

# 1. Load the CSV Data
try:
    df = pd.read_csv("waste_telemetry.csv")
except FileNotFoundError:
    print("Error: 'waste_telemetry.csv' not found. Run the main camera app and scan items first!")
    exit()

if df.empty:
    print("The CSV is empty. Please scan some items first!")
    exit()

# 2. Setup the Dark Cinematic Theme for the Dashboard
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.patch.set_facecolor('#121212') # Dark background to match your UI
text_color = '#E0E0E0'

# --- CHART 1: System Efficiency (Pie Chart) ---
status_counts = df['Status'].value_counts()

# Ensure Correct is Green and Contamination is Red
colors = ['#32FF64' if status == 'CORRECT' else '#FF3232' for status in status_counts.index]

ax1.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', 
        startangle=140, colors=colors, explode=[0.05]*len(status_counts),
        textprops={'color': text_color, 'fontsize': 12, 'weight': 'bold'},
        wedgeprops={'edgecolor': '#121212', 'linewidth': 2})
ax1.set_title("RecycloVision: System Efficiency", color='#008CFF', fontsize=16, weight='bold', pad=20)

# --- CHART 2: Top Waste Items (Bar Chart) ---
item_counts = df['Object_Detected'].value_counts().head(5) # Get top 5 most thrown items

bars = ax2.bar(item_counts.index, item_counts.values, color='#008CFF', edgecolor='#121212', linewidth=2)
ax2.set_title("Top 5 Objects Processed", color='#008CFF', fontsize=16, weight='bold', pad=20)
ax2.set_facecolor('#1E1E1E')
ax2.tick_params(axis='x', colors=text_color, labelsize=12)
ax2.tick_params(axis='y', colors=text_color, labelsize=12)

# Clean up the bar chart borders
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['bottom'].set_color('#333333')
ax2.spines['left'].set_color('#333333')

# 3. Save and display the dashboard
plt.tight_layout()
output_filename = "recyclovision_dashboard.png"
plt.savefig(output_filename, dpi=300, facecolor=fig.get_facecolor())

print(f"Success! High-resolution dashboard saved as: {output_filename}")
plt.show()