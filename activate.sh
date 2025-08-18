#!/bin/bash
# Mini-Ethereum Environment Setup Script

echo "🔧 Setting up Mini-Ethereum environment..."

# Activate the conda environment
source ~/opt/anaconda3/etc/profile.d/conda.sh
conda activate mini-ethereum

echo "✅ Environment activated! You can now run:"
echo "   python quick_test.py"
echo "   python example_usage.py"
echo "   python enhanced_cli.py --help"
echo "   python demo.py"
echo ""
echo "To deactivate later, run: conda deactivate"