rule get_month_of_data:
    input:
        script = "[tbd]"
    output:
        "data/[tbd]"
    params:
        file = [tbd]
    shell:
        """
        {input.script} {params.file}
        """
rule filter_month_of_data:
    input:
        script = "[tbd]"
    output:
        "data/[tbd]"
    params:
        file = [tbd]
    shell:
        """
        {input.script} {params.file}
        """
rule combine_filtered_months:
    input:
        script = "[tbd]"
    output:
        "data/[tbd]"
    params:
        file = [tbd]
    shell:
        """
        {input.script} {params.file}
        """

#the model will be trained in a separate, manually overseen process
rule apply_classification_model_to_data:
    input:
        script = "[tbd]"
    output:
        "data/[tbd]"
    params:
        file = [tbd]
    shell:
        """
        {input.script} {params.file}
        """
rule run_regression_on_data:
    input:
        script = "[tbd]"
    output:
        "data/[tbd]"
    params:
        file = [tbd]
    shell:
        """
        {input.script} {params.file}
        """
rule generate_visuals_from_regression:
    input:
        script = "[tbd]"
    output:
        "data/[tbd]"
    params:
        file = [tbd]
    shell:
        """
        {input.script} {params.file}
        """
