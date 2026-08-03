package com.nishita.jobportal.config;

import com.nishita.jobportal.entity.UserAccount;
import com.nishita.jobportal.repository.UserRepository;
import com.nimbusds.jose.jwk.source.ImmutableSecret;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.*;
import org.springframework.security.authentication.*;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.*;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.jwt.*;
import org.springframework.security.oauth2.server.resource.authentication.*;
import org.springframework.security.web.SecurityFilterChain;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.util.List;

@Configuration @EnableMethodSecurity
public class SecurityConfig {
 @Value("${app.jwt-secret}") private String secret;
 @Bean PasswordEncoder passwordEncoder(){return new BCryptPasswordEncoder();}
 @Bean UserDetailsService userDetailsService(UserRepository users){return email->{UserAccount u=users.findByEmailIgnoreCase(email).orElseThrow(()->new UsernameNotFoundException(email));return new User(u.getEmail(),u.getPasswordHash(),List.of(new SimpleGrantedAuthority("ROLE_"+u.getRole().name())));};}
 @Bean AuthenticationManager authenticationManager(UserDetailsService uds,PasswordEncoder encoder){DaoAuthenticationProvider p=new DaoAuthenticationProvider(uds);p.setPasswordEncoder(encoder);return new ProviderManager(p);}
 @Bean JwtDecoder jwtDecoder(){byte[] key=secret.getBytes(StandardCharsets.UTF_8);return NimbusJwtDecoder.withSecretKey(new SecretKeySpec(key,"HmacSHA256")).build();}
 @Bean JwtEncoder jwtEncoder(){return new NimbusJwtEncoder(new ImmutableSecret<>(secret.getBytes(StandardCharsets.UTF_8)));}
 @Bean JwtAuthenticationConverter jwtAuthenticationConverter(){JwtGrantedAuthoritiesConverter c=new JwtGrantedAuthoritiesConverter();c.setAuthoritiesClaimName("roles");c.setAuthorityPrefix("ROLE_");JwtAuthenticationConverter converter=new JwtAuthenticationConverter();converter.setJwtGrantedAuthoritiesConverter(c);return converter;}
 @Bean SecurityFilterChain filterChain(HttpSecurity http,JwtAuthenticationConverter converter)throws Exception{return http.csrf(csrf->csrf.disable()).sessionManagement(s->s.sessionCreationPolicy(SessionCreationPolicy.STATELESS)).authorizeHttpRequests(a->a.requestMatchers("/","/index.html","/styles.css","/app.js","/api/auth/**","/api/jobs/**","/swagger-ui/**","/swagger-ui.html","/v3/api-docs/**").permitAll().anyRequest().authenticated()).oauth2ResourceServer(o->o.jwt(j->j.jwtAuthenticationConverter(converter))).build();}
}
