def save_report(report: list, output_report_path: str) -> None:
    """
    Save the analysis report to a text file.

    Args:
        report (list): List of report lines.
        output_report_path (str): Path to save the report.
    """
    with open(output_report_path, 'w') as f:
        f.write("\n".join(report))
