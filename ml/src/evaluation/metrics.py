"""
Model evaluation metrics and utilities
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    roc_auc_score,
    precision_recall_curve,
    average_precision_score
)


def evaluate_regression(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, float]:
    """
    Evaluate regression metrics
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        Dictionary of metrics
    """
    metrics = {
        'mse': mean_squared_error(y_true, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
        'mae': mean_absolute_error(y_true, y_pred),
        'r2': r2_score(y_true, y_pred),
        'mape': np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100
    }
    
    return metrics


def evaluate_classification(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    threshold: float = 0.5
) -> Dict[str, float]:
    """
    Evaluate classification metrics
    
    Args:
        y_true: True binary labels
        y_pred_proba: Predicted probabilities
        threshold: Classification threshold
        
    Returns:
        Dictionary of metrics
    """
    y_pred_binary = (y_pred_proba >= threshold).astype(int)
    
    tp = np.sum((y_true == 1) & (y_pred_binary == 1))
    fp = np.sum((y_true == 0) & (y_pred_binary == 1))
    tn = np.sum((y_true == 0) & (y_pred_binary == 0))
    fn = np.sum((y_true == 1) & (y_pred_binary == 0))
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    metrics = {
        'accuracy': (tp + tn) / len(y_true),
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'roc_auc': roc_auc_score(y_true, y_pred_proba) if len(np.unique(y_true)) > 1 else 0,
        'avg_precision': average_precision_score(y_true, y_pred_proba) if len(np.unique(y_true)) > 1 else 0
    }
    
    return metrics


def evaluate_spatial_performance(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    locations: np.ndarray
) -> pd.DataFrame:
    """
    Evaluate performance by spatial region
    
    Args:
        y_true: True values
        y_pred: Predicted values
        locations: (N, 2) array of (lat, lon)
        
    Returns:
        DataFrame with spatial metrics
    """
    # Create spatial bins (e.g., 5 degree grid)
    lat_bins = np.arange(
        locations[:, 0].min(),
        locations[:, 0].max() + 5,
        5
    )
    lon_bins = np.arange(
        locations[:, 1].min(),
        locations[:, 1].max() + 5,
        5
    )
    
    lat_indices = np.digitize(locations[:, 0], lat_bins)
    lon_indices = np.digitize(locations[:, 1], lon_bins)
    
    results = []
    
    for lat_idx in np.unique(lat_indices):
        for lon_idx in np.unique(lon_indices):
            mask = (lat_indices == lat_idx) & (lon_indices == lon_idx)
            
            if mask.sum() > 0:
                region_metrics = evaluate_regression(
                    y_true[mask],
                    y_pred[mask]
                )
                region_metrics['lat_bin'] = lat_bins[lat_idx - 1]
                region_metrics['lon_bin'] = lon_bins[lon_idx - 1]
                region_metrics['n_samples'] = mask.sum()
                
                results.append(region_metrics)
    
    return pd.DataFrame(results)


def evaluate_temporal_performance(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    timestamps: pd.DatetimeIndex
) -> pd.DataFrame:
    """
    Evaluate performance by time period
    
    Args:
        y_true: True values
        y_pred: Predicted values
        timestamps: Timestamps for each prediction
        
    Returns:
        DataFrame with temporal metrics
    """
    df = pd.DataFrame({
        'y_true': y_true,
        'y_pred': y_pred,
        'timestamp': timestamps
    })
    
    df['month'] = df['timestamp'].dt.month
    df['year'] = df['timestamp'].dt.year
    
    results = []
    
    for (year, month), group in df.groupby(['year', 'month']):
        if len(group) > 0:
            metrics = evaluate_regression(
                group['y_true'].values,
                group['y_pred'].values
            )
            metrics['year'] = year
            metrics['month'] = month
            metrics['n_samples'] = len(group)
            
            results.append(metrics)
    
    return pd.DataFrame(results)


def calculate_feature_importance(
    model,
    feature_names: list,
    method: str = "gain"
) -> pd.DataFrame:
    """
    Calculate feature importance
    
    Args:
        model: Trained model
        feature_names: List of feature names
        method: Importance method ('gain', 'split', 'weight')
        
    Returns:
        DataFrame with feature importances
    """
    # Try to get importance from model
    importance = None
    
    # XGBoost
    if hasattr(model, 'get_score'):
        importance_dict = model.get_score(importance_type=method)
        importance = [importance_dict.get(f, 0) for f in feature_names]
    
    # LightGBM
    elif hasattr(model, 'feature_importance'):
        importance = model.feature_importance(importance_type=method)
    
    # scikit-learn
    elif hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
    
    if importance is None:
        return pd.DataFrame({
            'feature': feature_names,
            'importance': [0] * len(feature_names)
        })
    
    df = pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    })
    
    df = df.sort_values('importance', ascending=False).reset_index(drop=True)
    
    return df


def generate_evaluation_report(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str = "Model"
) -> str:
    """
    Generate a comprehensive evaluation report
    
    Args:
        y_true: True values
        y_pred: Predicted values
        model_name: Name of the model
        
    Returns:
        Formatted report string
    """
    metrics = evaluate_regression(y_true, y_pred)
    
    report = f"""
    ============================================
    Evaluation Report: {model_name}
    ============================================
    
    Regression Metrics:
    -------------------
    MSE:  {metrics['mse']:.4f}
    RMSE: {metrics['rmse']:.4f}
    MAE:  {metrics['mae']:.4f}
    R²:   {metrics['r2']:.4f}
    MAPE: {metrics['mape']:.2f}%
    
    Sample Statistics:
    ------------------
    N samples: {len(y_true)}
    True mean: {y_true.mean():.4f}
    Pred mean: {y_pred.mean():.4f}
    True std:  {y_true.std():.4f}
    Pred std:  {y_pred.std():.4f}
    
    ============================================
    """
    
    return report
