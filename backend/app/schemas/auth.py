from pydantic import BaseModel, EmailStr, Field, model_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")

        if not any(char.isupper() for char in self.password):
            raise ValueError(
                "Password must contain at least one uppercase letter."
            )

        if not any(char.isdigit() for char in self.password):
            raise ValueError(
                "Password must contain at least one digit."
            )

        return self


class RegisterResponse(BaseModel):
    message: str
    email: EmailStr
