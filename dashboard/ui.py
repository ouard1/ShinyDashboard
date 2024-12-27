from shiny import ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        title="Crude Oil Dashboard",
        fillable=False,
        bg="#851c44"  
    ),

    ui.div(
        ui.div(
            ui.div(
                ui.output_ui("year_selected"),
                style="margin-right: 10px; flex: 1; max-width: 200px;" 
            ),
            ui.div(
                ui.output_ui("month_selected"),
                style="flex: 1; max-width: 200px;" 
            ),
            style="display: flex; flex-direction: row; align-items: center; gap: 10px; margin-bottom: 10px; margin-top: -20px; margin-left: -10px;"  
        ),
        ui.div(
            ui.output_ui("price_plot"),
            style="margin-top: 60px; margin-left: -20px; width: 600px; height: 200px; position: absolute; top: 10px; left: 10px;" 
        ),
        ui.div(
            ui.card(
                ui.card_header("Live Currency Exchange Rates for 1 USD", style="text-align: center; font-size: 18px;"),
                ui.output_ui("card_forex"),
                style="position: fixed; right: 30px; top: 20px; width: 350px; height: 350px; padding: 10px; border-radius: 10px; border: 4px solid #851c44;"
            ),
        ),
        style="position: relative; width: 100%; height: auto;", 
    )
)




