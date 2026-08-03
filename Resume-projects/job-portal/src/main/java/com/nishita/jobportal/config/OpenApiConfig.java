package com.nishita.jobportal.config;
import io.swagger.v3.oas.models.*;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.security.*;
import org.springframework.context.annotation.*;
@Configuration public class OpenApiConfig{
 @Bean OpenAPI jobPortalApi(){return new OpenAPI().info(new Info().title("Job Portal API").version("1.0").description("Candidate and recruiter workflows for the Job Portal MVP")).components(new Components().addSecuritySchemes("bearerAuth",new SecurityScheme().type(SecurityScheme.Type.HTTP).scheme("bearer").bearerFormat("JWT"))).addSecurityItem(new SecurityRequirement().addList("bearerAuth"));}
}
