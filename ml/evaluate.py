"""
Model evaluation - AUC-PR, Brier score, reliability diagrams, ECE
"""
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score, brier_score_loss,
    precision_recall_curve, roc_auc_score
)
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Any


def compute_metrics(
    y_true: np.ndarray,
    probas: np.ndarray
) -> Dict[str, float]:
    """
    Compute evaluation metrics.
    
    Args:
        y_true: True labels
        probas: Predicted probabilities
    
    Returns:
        Dictionary of metrics
    """
    metrics = {
        'auc_pr': average_precision_score(y_true, probas),
        'auc_roc': roc_auc_score(y_true, probas),
        'brier': brier_score_loss(y_true, probas),
        'ece': compute_ece(y_true, probas)
    }
    
    return metrics


def compute_ece(
    y_true: np.ndarray,
    probas: np.ndarray,
    n_bins: int = 10
) -> float:
    """
    Compute Expected Calibration Error (ECE).
    
    Args:
        y_true: True labels
        probas: Predicted probabilities
        n_bins: Number of bins
    
    Returns:
        ECE value
    """
    bin_edges = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    
    for i in range(n_bins):
        mask = (probas >= bin_edges[i]) & (probas < bin_edges[i + 1])
        if i == n_bins - 1:
            mask = (probas >= bin_edges[i]) & (probas <= bin_edges[i + 1])
        
        if mask.sum() > 0:
            bin_accuracy = y_true[mask].mean()
            bin_confidence = probas[mask].mean()
            bin_weight = mask.sum() / len(y_true)
            
            ece += bin_weight * abs(bin_accuracy - bin_confidence)
    
    return ece


def plot_reliability_diagram(
    y_true: np.ndarray,
    probas: np.ndarray,
    output_path: str,
    n_bins: int = 10
):
    """
    Plot reliability diagram.
    
    Args:
        y_true: True labels
        probas: Predicted probabilities
        output_path: Path to save plot
        n_bins: Number of bins
    """
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    bin_probas = []
    bin_observed = []
    
    for i in range(n_bins):
        mask = (probas >= bin_edges[i]) & (probas < bin_edges[i + 1])
        if i == n_bins - 1:
            mask = (probas >= bin_edges[i]) & (probas <= bin_edges[i + 1])
        
        if mask.sum() > 0:
            bin_probas.append(probas[mask].mean())
            bin_observed.append(y_true[mask].mean())
        else:
            bin_probas.append(np.nan)
            bin_observed.append(np.nan)
    
    # Plot
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Perfect calibration line
    ax.plot([0, 1], [0, 1], 'k--', label='Perfect calibration')
    
    # Actual calibration
    mask = ~np.isnan(bin_probas)
    ax.plot(
        np.array(bin_probas)[mask],
        np.array(bin_observed)[mask],
        'o-',
        label='Model'
    )
    
    ax.set_xlabel('Predicted Probability')
    ax.set_ylabel('Observed Frequency')
    ax.set_title('Reliability Diagram')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved reliability diagram to {output_path}")


def plot_pr_curve(
    y_true: np.ndarray,
    probas: np.ndarray,
    output_path: str
):
    """
    Plot precision-recall curve.
    
    Args:
        y_true: True labels
        probas: Predicted probabilities
        output_path: Path to save plot
    """
    precision, recall, _ = precision_recall_curve(y_true, probas)
    auc_pr = average_precision_score(y_true, probas)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.plot(recall, precision, label=f'AUC-PR = {auc_pr:.3f}')
    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')
    ax.set_title('Precision-Recall Curve')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved PR curve to {output_path}")


def evaluate_per_region(
    y_true: np.ndarray,
    probas: np.ndarray,
    regions: np.ndarray
) -> pd.DataFrame:
    """
    Evaluate model per region.
    
    Args:
        y_true: True labels
        probas: Predicted probabilities
        regions: Region IDs
    
    Returns:
        DataFrame with metrics per region
    """
    results = []
    
    for region_id in np.unique(regions):
        mask = regions == region_id
        region_metrics = compute_metrics(y_true[mask], probas[mask])
        region_metrics['region'] = region_id
        region_metrics['n_samples'] = mask.sum()
        region_metrics['positive_rate'] = y_true[mask].mean()
        
        results.append(region_metrics)
    
    return pd.DataFrame(results)


def save_metrics(metrics: Dict[str, Any], output_path: str):
    """Save metrics to CSV"""
    if isinstance(metrics, dict):
        df = pd.DataFrame([metrics])
    else:
        df = metrics
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"Saved metrics to {output_path}")


if __name__ == "__main__":
    print("Evaluation Script")
    
    # Example with synthetic data
    n_samples = 5000
    probas = np.random.beta(2, 5, n_samples)
    y_true = (np.random.rand(n_samples) < probas).astype(int)
    regions = np.random.choice([0, 1, 2], n_samples)
    
    # Compute overall metrics
    print("\nOverall metrics:")
    metrics = compute_metrics(y_true, probas)
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")
    
    # Per-region metrics
    print("\nPer-region metrics:")
    region_metrics = evaluate_per_region(y_true, probas, regions)
    print(region_metrics.to_string(index=False))
    
    # Create output directory
    output_dir = Path('/tmp/artifacts')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Plot reliability diagram
    plot_reliability_diagram(y_true, probas, str(output_dir / 'reliability.png'))
    
    # Plot PR curve
    plot_pr_curve(y_true, probas, str(output_dir / 'pr_curve.png'))
    
    # Save metrics
    save_metrics(metrics, str(output_dir / 'metrics.csv'))
    save_metrics(region_metrics, str(output_dir / 'metrics_per_region.csv'))
    
    print("\nEvaluation complete!")
