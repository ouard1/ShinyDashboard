from shiny import ui


app_ui = ui.page_fluid(
    ui.div(
        ui.h3("Crude Oil Dashboard", style="text-align: left ; color: #fff; margin: 0;"),
        style="background-color: #6a1636; padding: 20px; font-size: 22px;"
    ),
    
  
    ui.div(
        ui.div(
            ui.output_ui("card_forex"),
            style="margin: 20px;"
        )
    ),

    
    ui.div(
        ui.div(
            ui.div(
                ui.div(
                    ui.output_ui("year_selected"),
                    style="margin-right: 10px;"
                ),
                ui.div(
                    ui.output_ui("month_selected"),
                    style="margin-right: 10px;"
                ),
                style="display: flex; flex-direction: row; justify-content: flex-start; gap: 20px; padding: 10px;"
            ),
            ui.div(
                ui.output_ui("price_plot"),
                style="flex: 1; display: flex; flex-direction: column; align-items: flex-start; padding: 20px;   margin-bottom: 20px; width: 100%;"
            ),
        ),
    ),

   
    ui.div(
        ui.div(
            ui.div(
                ui.output_ui("region_selector"),
                style="margin-right: 10px;"
            ),
            ui.div(
                ui.output_ui("variable_selector"),
                style="margin-right: 10px;"
            ),
            style="display: flex; flex-direction: row; justify-content: flex-start; gap: 40px; padding: 10px; margin-left: 20px"
        ),
        ui.div(
            ui.div(
                ui.output_ui("correlation_plot"),
                style="padding: 20px; background-color: #f9f9f9; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); flex: 1; width: 100%;"
            ),
            ui.div(
                ui.output_ui("correlation_heatmap"),
                style="flex: 1; padding: 20px; background-color: #f9f9f9; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); width: 100%; max-width: 800px;height : 100% ; height: 600px; overflow: hidden;"
            ),
            style="display: flex; flex-direction: row; gap: 40px; padding: 10px; flex-wrap: wrap; justify-content: space-between;"
        ),
    ),

    style="padding: 20px; max-width: 1900px; margin: 0 auto;"
)
