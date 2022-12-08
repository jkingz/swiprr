from rest_framework.exceptions import APIException


class OwnerShipTypeDoesNotExists(APIException):
    # Raise this error when a frontend passes a data that tries to request
    # an ownership type with an invalid id

    status_code = 400
    default_detail = "Invalid ownership type is passed"
    default_code = "ownership_type_does_not_exists"


class TransactionTypeDoesNotExists(APIException):
    # Raise this error when a frontend passes a data that tries to request
    # an transaction type with an invalid id

    status_code = 400
    default_detail = "Invalid transaction type is passed"
    default_code = "transaction_type_does_not_exists"


class ParkingTypeDoesNotExists(APIException):
    # Raise this error when a frontend passes a data that tries to request
    # an parking type with an invalid id

    status_code = 400
    default_detail = "Invalid parking type is passed"
    default_code = "parking_type_does_not_exists"


class LngAndLatIsNotPassed(APIException):
    # Raise this error when a frontend passes a data that tries to request
    # without lng and lat

    status_code = 400
    default_detail = "Longtitude and latitude is not passed"
    default_code = "lng_and_lat_is_not_passed"


class ParameterFormatTypeNotExpected(APIException):
    # Return 400, instead of 500 if the exepcted variable type does not match
    # expected format

    status_code = 400
    default_detail = (
        "The format type that's been passed on does not match expected format"
    )
    default_code = "invalid_parameter_format"

    def __init__(self, *agrs, **kwargs):
        # Pop custom fields here
        param_name = kwargs.pop("param_name", None)
        var_type = kwargs.pop("var_type", None)

        if param_name and var_type:
            self.default_detail = (
                f"The format type that's been passed on '{param_name}'"
                + f"does not match expected format, '{var_type}'"
            )

        return super().__init__(*agrs, **kwargs)
