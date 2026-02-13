from app.presentation.api.schemas import AllFlightsResponse, FlightResponse


class TestFlightService:
    def test_get_all_success(self, flight_service, mock_flight_connector):
        page = 1
        size = 10
        
        expected_response = AllFlightsResponse(
            page=1,
            pageSize=10,
            totalElements=1,
            items=[
                FlightResponse(
                    flightNumber="AFL031",
                    fromAirport="Санкт-Петербург Пулково",
                    toAirport="Москва Шереметьево",
                    date="2021-10-08 20:00",
                    price=1500,
                )
            ],
        )
        
        mock_flight_connector.get_flights.return_value = expected_response
        
        result = flight_service.get_all(page, size)
        
        mock_flight_connector.get_flights.assert_called_once_with(page, size)
        assert isinstance(result, AllFlightsResponse)
        assert result.page == expected_response.page
        assert result.pageSize == expected_response.pageSize
        assert result.totalElements == expected_response.totalElements
        assert len(result.items) == 1
        assert result.items[0].flightNumber == "AFL031"

    def test_get_all_empty(self, flight_service, mock_flight_connector):
        page = 1
        size = 10
        
        expected_response = AllFlightsResponse(
            page=1,
            pageSize=10,
            totalElements=0,
            items=[],
        )
        
        mock_flight_connector.get_flights.return_value = expected_response
        
        result = flight_service.get_all(page, size)
        
        mock_flight_connector.get_flights.assert_called_once_with(page, size)
        assert isinstance(result, AllFlightsResponse)
        assert result.totalElements == 0
        assert len(result.items) == 0
