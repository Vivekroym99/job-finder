#!/bin/bash

echo "=================================================="
echo "JOB FINDER - Automated Job Search & Matching Tool"
echo "=================================================="
echo ""
echo "Configuration:"
echo "- Resume: /workspaces/job-finder/resume/resume.md"
echo "- Location: Poland (all cities + remote)"
echo "- Min Match: 70%"
echo "- Max Age: 14 days"
echo "- Output: /mnt/data/"
echo ""
echo "Usage Examples:"
echo "./run_job_search.sh --location Warsaw"
echo "./run_job_search.sh --location Krakow --no-remote"
echo "./run_job_search.sh --location Poland --min-match 60"
echo "./run_job_search.sh --location Warsaw --linkedin-basic"
echo ""

# Create output directory if it doesn't exist
OUTPUT_DIR="/tmp/job_search_results"
mkdir -p "$OUTPUT_DIR"

# Run the job search automation
cd /workspaces/job-finder/job_search_automation
python main.py --output-dir "$OUTPUT_DIR" "$@"