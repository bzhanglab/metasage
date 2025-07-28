import numpy as np
import seaborn as sns

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm


def plot_max_weighted(shap_values, feat_names, save_to: str, num_features=15):
    sns.set_theme(context="talk", style="white")

    # Normalize SHAP values by the max absolute value for each sample
    normalized_shap_values = shap_values / np.abs(shap_values).max(
        axis=1, keepdims=True
    )
    # Calculate the mean of the normalized SHAP values for each feature
    mean_normalized_shap_values = np.mean(np.abs(normalized_shap_values), axis=0)

    # mean_shap = np.mean(np.abs(shap_values), axis=0)
    # mean_normalized_shap_values = mean_shap / mean_shap.max()

    # Get the indices of the top features
    top_features_indices = np.argsort(mean_normalized_shap_values)[-num_features:][::-1]

    # Get the top features and their mean normalized SHAP values
    top_features = [feat_names[i] for i in top_features_indices]
    top_mean_normalized_shap_values = mean_normalized_shap_values[top_features_indices]

    # Create a horizontal bar plot
    plt.figure(figsize=(10, 8))
    ax = sns.barplot(x=top_mean_normalized_shap_values, y=top_features, orient="h")
    ax.bar_label(ax.containers[0], fontsize=12, fmt="%.2f")
    plt.xlabel("Average Max Normalized SHAP Value")
    plt.ylabel("Feature")
    plt.title("Top Features by Average Max Normalized SHAP Value")
    plt.tight_layout()
    plt.savefig(save_to)
    plt.close()


def new_plot_max_weighted(
    shap_values, feature_values, feat_names, save_to: str, num_features=15
):
    """
    Create a horizontal bar plot of SHAP values with tightly packed boxes representing individual samples.

    Parameters:
    - shap_values: 2D numpy array of SHAP values (samples x features)
    - feature_values: 2D numpy array of feature values (samples x features)
    - feat_names: List of feature names
    - save_to: Path to save the figure
    - num_features: Number of top features to display
    """
    # Handle potential null values
    shap_values = np.nan_to_num(shap_values, 0)
    feature_values = np.nan_to_num(feature_values, np.nan)

    # Normalize SHAP values by the max absolute value for each sample (maintaining direction)
    normalized_shap_values = shap_values / np.abs(shap_values).max(
        axis=1, keepdims=True
    )

    # Calculate the mean of the normalized SHAP values for each feature
    mean_normalized_shap_values = np.mean(np.abs(normalized_shap_values), axis=0)

    # Get the indices of the top features
    top_features_indices = np.argsort(mean_normalized_shap_values)[-num_features:]

    # Get the top features, their mean normalized SHAP values, and corresponding feature values
    top_features = [feat_names[i] for i in top_features_indices]
    top_mean_normalized_shap_values = mean_normalized_shap_values[top_features_indices]
    top_shap_values = normalized_shap_values[:, top_features_indices]
    top_feature_values = feature_values[:, top_features_indices]

    # Create the figure and axis with more vertical space
    plt.figure(figsize=(12, 15))

    # Create a color map (blue to red)
    cmap = plt.cm.coolwarm

    # Plot each feature as a collection of sample boxes
    for i, (feature, mean_shap) in enumerate(
        zip(top_features, top_mean_normalized_shap_values)
    ):
        # Sort samples for this feature based on SHAP values (negative values first)
        sample_order = np.argsort(top_shap_values[:, i])
        feature_values_for_feature = top_feature_values[sample_order, i]

        feature_values_centered = feature_values_for_feature - np.nanmedian(
            feature_values_for_feature
        )
        feature_norm = (
            feature_values_centered
            - feature_values_centered[~np.isnan(feature_values_centered)].min()
        ) / (
            feature_values_centered[~np.isnan(feature_values_centered)].max()
            - feature_values_centered[~np.isnan(feature_values_centered)].min()
        )

        # Normalize feature values for color mapping
        # feature_norm = (
        #     top_feature_values[sample_order, i] - top_feature_values[:, i].min()
        # ) / (top_feature_values[:, i].max() - top_feature_values[:, i].min())

        # feature_norm = top_feature_values[sample_order, i] - np.median(
        #     top_feature_values[sample_order, i]
        # ) / (
        #     top_feature_values[sample_order, i].max()
        #     - top_feature_values[sample_order, i].min()
        #     - 2 * np.median(top_feature_values[sample_order, i])
        # )
        # Normalize sample SHAP values to sum up to the mean SHAP value
        sample_shap_abs = np.abs(top_shap_values[sample_order, i])
        normalized_sample_shap = sample_shap_abs / sample_shap_abs.sum() * mean_shap

        # Plot boxes for each sample
        current_width = 0
        for j, (sample_shap, color_norm, orig_feature_val) in enumerate(
            zip(
                normalized_sample_shap,
                feature_norm,
                top_feature_values[sample_order, i],
            )
        ):
            # Determine color and height
            if np.isnan(orig_feature_val):
                # Gray for null values
                box_color = "gray"
                box_height = abs(top_shap_values[sample_order, i][j]) + 0.1
            else:
                # Color based on feature value
                box_color = cmap(color_norm)
                # Height proportional to the max normalized value
                box_height = (
                    abs(top_shap_values[sample_order, i][j]) + 0.1
                )  # Add small buffer

            # Plot individual box horizontally
            plt.barh(
                feature,
                sample_shap,
                left=current_width,
                height=box_height * 0.9,
                color=box_color,
                edgecolor="none",
                linewidth=0.5,
            )

            # Update current width
            current_width += sample_shap

    # Customize the plot
    plt.ylabel("Feature")
    plt.xlabel("Mean Normalized SHAP Value")
    plt.title("Top Features by Average Max Normalized SHAP Value")
    plt.tight_layout()

    # Save the figure
    plt.savefig(save_to)
    plt.close()


def done_new_plot_max_weighted(
    shap_values, feature_values, feat_names, save_to: str, num_features=15
):
    """
    Create a vertical bar plot of SHAP values with tightly packed boxes representing individual samples.

    Parameters:
    - shap_values: 2D numpy array of SHAP values (samples x features)
    - feature_values: 2D numpy array of feature values (samples x features)
    - feat_names: List of feature names
    - save_to: Path to save the figure
    - num_features: Number of top features to display
    """
    # Handle potential null values
    shap_values = np.nan_to_num(shap_values, 0)
    feature_values = np.nan_to_num(feature_values, np.nan)

    # Normalize SHAP values by the max absolute value for each sample (maintaining direction)
    normalized_shap_values = shap_values / np.abs(shap_values).max(
        axis=1, keepdims=True
    )

    # Calculate the mean of the normalized SHAP values for each feature
    mean_normalized_shap_values = np.mean(np.abs(normalized_shap_values), axis=0)

    # Get the indices of the top features
    top_features_indices = np.argsort(mean_normalized_shap_values)[-num_features:][::-1]

    # Get the top features, their mean normalized SHAP values, and corresponding feature values
    top_features = [feat_names[i] for i in top_features_indices]
    top_mean_normalized_shap_values = mean_normalized_shap_values[top_features_indices]
    top_shap_values = normalized_shap_values[:, top_features_indices]
    top_feature_values = feature_values[:, top_features_indices]

    # Create the figure and axis
    plt.figure(figsize=(12, 10))

    # Create a color map (blue to red)
    cmap = plt.cm.coolwarm

    # Plot each feature as a collection of sample boxes
    for i, (feature, mean_shap) in enumerate(
        zip(top_features, top_mean_normalized_shap_values)
    ):
        # Sort samples for this feature based on SHAP values (negative values first)
        sample_order = np.argsort(top_shap_values[:, i])

        # Normalize feature values for color mapping
        feature_norm = (
            top_feature_values[sample_order, i] - top_feature_values[:, i].min()
        ) / (top_feature_values[:, i].max() - top_feature_values[:, i].min())

        # Normalize sample SHAP values to sum up to the mean SHAP value
        sample_shap_abs = np.abs(top_shap_values[sample_order, i])
        normalized_sample_shap = sample_shap_abs / sample_shap_abs.sum() * mean_shap

        # Plot boxes for each sample
        current_height = 0
        for j, (sample_shap, color_norm, orig_feature_val) in enumerate(
            zip(
                normalized_sample_shap,
                feature_norm,
                top_feature_values[sample_order, i],
            )
        ):
            # Determine color and width
            if np.isnan(orig_feature_val):
                # Gray for null values
                box_color = "gray"
                box_width = 1  # Default width for nulls
            else:
                # Color based on feature value
                box_color = cmap(color_norm)
                # Width proportional to the max normalized value
                box_width = (
                    abs(top_shap_values[sample_order, i][j]) + 0.1
                )  # Add small buffer

            # Plot individual box
            plt.bar(
                feature,
                sample_shap,
                bottom=current_height,
                width=box_width,
                color=box_color,
                edgecolor="none",
                linewidth=0.5,
            )

            # Update current height
            current_height += sample_shap

    # Customize the plot
    plt.xlabel("Feature")
    plt.ylabel("Mean Normalized SHAP Value")
    plt.title("Top Features by Average Max Normalized SHAP Value")
    plt.xticks(range(len(top_features)), top_features, rotation=45, ha="right")
    plt.tight_layout()

    # Save the figure
    plt.savefig(save_to)
    plt.close()


def good_new_plot_max_weighted(
    shap_values, feature_values, feat_names, save_to: str, num_features=15
):
    """
    Create a vertical bar plot of SHAP values with tightly packed boxes representing individual samples.

    Parameters:
    - shap_values: 2D numpy array of SHAP values (samples x features)
    - feature_values: 2D numpy array of feature values (samples x features)
    - feat_names: List of feature names
    - save_to: Path to save the figure
    - num_features: Number of top features to display
    """
    # Normalize SHAP values by the max absolute value for each sample (maintaining direction)
    normalized_shap_values = shap_values / np.abs(shap_values).max(
        axis=1, keepdims=True
    )

    # Calculate the mean of the normalized SHAP values for each feature
    mean_normalized_shap_values = np.mean(np.abs(normalized_shap_values), axis=0)

    # Get the indices of the top features
    top_features_indices = np.argsort(mean_normalized_shap_values)[-num_features:][::-1]

    # Get the top features, their mean normalized SHAP values, and corresponding feature values
    top_features = [feat_names[i] for i in top_features_indices]
    top_mean_normalized_shap_values = mean_normalized_shap_values[top_features_indices]
    top_shap_values = normalized_shap_values[:, top_features_indices]
    top_feature_values = feature_values[:, top_features_indices]

    # Create the figure and axis
    plt.figure(figsize=(12, 10))

    # Create a color map (blue to red)
    cmap = plt.cm.coolwarm

    # Plot each feature as a collection of sample boxes
    for i, (feature, mean_shap) in enumerate(
        zip(top_features, top_mean_normalized_shap_values)
    ):
        # Sort samples for this feature based on SHAP values (negative values first)
        sample_order = np.argsort(top_shap_values[:, i])

        # Normalize feature values for color mapping
        feature_norm = (
            top_feature_values[sample_order, i] - top_feature_values[:, i].min()
        ) / (top_feature_values[:, i].max() - top_feature_values[:, i].min())

        # Normalize sample SHAP values to sum up to the mean SHAP value
        sample_shap_abs = np.abs(top_shap_values[sample_order, i])
        normalized_sample_shap = sample_shap_abs / sample_shap_abs.sum() * mean_shap

        # Plot boxes for each sample
        current_height = 0
        for j, (sample_shap, color_norm) in enumerate(
            zip(normalized_sample_shap, feature_norm)
        ):
            # Color based on feature value
            box_color = cmap(color_norm)

            # Plot individual box
            plt.bar(
                feature,
                sample_shap,
                bottom=current_height,
                width=1,
                color=box_color,
                edgecolor="none",
                linewidth=0,
            )

            # Update current height
            current_height += sample_shap

    # Customize the plot
    plt.xlabel("Feature")
    plt.ylabel("Mean Normalized SHAP Value")
    plt.title("Top Features by Average Max Normalized SHAP Value")
    plt.xticks(range(len(top_features)), top_features, rotation=45, ha="right")
    plt.tight_layout()

    # Save the figure
    plt.savefig(save_to)
    plt.close()


# Example usage:
# plot_max_weighted(shap_values, feature_values, feature_names, 'shap_plot.png')
