package com.nishita.jobportal.exception;
import org.springframework.http.*;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;
import java.time.Instant;
import java.util.*;
@RestControllerAdvice
public class ApiExceptionHandler {
 record ErrorBody(Instant timestamp,int status,String error,Object details){}
 @ExceptionHandler(NotFoundException.class) ResponseEntity<ErrorBody> notFound(NotFoundException e){return body(HttpStatus.NOT_FOUND,e.getMessage());}
 @ExceptionHandler(ConflictException.class) ResponseEntity<ErrorBody> conflict(ConflictException e){return body(HttpStatus.CONFLICT,e.getMessage());}
 @ExceptionHandler(IllegalArgumentException.class) ResponseEntity<ErrorBody> bad(IllegalArgumentException e){return body(HttpStatus.BAD_REQUEST,e.getMessage());}
 @ExceptionHandler(MethodArgumentNotValidException.class) ResponseEntity<ErrorBody> validation(MethodArgumentNotValidException e){Map<String,String> fields=new LinkedHashMap<>();e.getBindingResult().getFieldErrors().forEach(x->fields.put(x.getField(),x.getDefaultMessage()));return new ResponseEntity<>(new ErrorBody(Instant.now(),400,"Validation failed",fields),HttpStatus.BAD_REQUEST);}
 private ResponseEntity<ErrorBody> body(HttpStatus status,String message){return new ResponseEntity<>(new ErrorBody(Instant.now(),status.value(),message,null),status);}
}
