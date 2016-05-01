class DynaWizard():
    def get(self, step=None):
        # Get form class for step.
        # Generate form kwargs.
        # Alter form kwargs.
        # Instantiate form.
        # Generate render context.
        pass

    def render_step(self, step):
        # Alter render context.
        # Get template.
        # Render template.
        pass

    def post(self, step=None):
        # Get form class for step.
        # Generate form kwargs.
        # Alter form kwargs.
        # Instantiate form.
        # If form is invalid:
            # render step
        # Update history.
        # Get next step.
        # if not next_step:
            # self.done()
        # else:
            # Redirect to next_step.
        pass
